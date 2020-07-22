/**
 * Make tooltips appear on hover over seats.
 */
function init_seat_tooltips() {
  document.querySelectorAll('.seat-with-tooltip')
    .forEach(function(seatContainer) {
      seatContainer.addEventListener('mouseover', function() {
        const dataset = seatContainer.dataset;

        let tooltipHTML = '<div class="seat-label">' + dataset.label + '</div>';

        const ticketId = dataset.ticketId;
        if (ticketId !== undefined) {
          if (seatContainer.querySelector('.seat').classList.contains('seat--managed')) {
            const ticketCode = document
              .getElementById('ticket-selection')
              .querySelector('.ticket[data-id="' + ticketId + '"]')
              .dataset.code;

            tooltipHTML += '<div class="seat-ticket-code"><span class="dimmed">Ticket:</span> <strong>' + ticketCode + '</strong></div>';
          }

          const occupierName = dataset.occupierName;
          if (occupierName !== undefined) {
            tooltipHTML += '<div class="seat-occupier">'
                         + '<div class="seat-occupier-avatar"><div class="avatar size-48"><img src="' + dataset.occupierAvatar + '"></div></div>'
                         + '<div class="seat-occupier-name"><span class="dimmed">reserviert von</span><br><strong>' + escape_html(occupierName) + '</strong></div>'
                         + '</div>';
          }
        }

        const tooltipNode = document.createElement('div');
        tooltipNode.classList.add('seat-tooltip');
        tooltipNode.innerHTML = tooltipHTML;
        seatContainer.appendChild(tooltipNode);
      });

      seatContainer.addEventListener('mouseout', function() {
        const tooltip = seatContainer.querySelector('.seat-tooltip');
        // Tooltip element won't exist at this point if the mouse
        // cursor is above a seat when the page is reloaded, so the
        // 'mouseout' event will fire upon mouse move even though no
        // 'mouseover' has occurred, thus no tooltip has been
        // generated that could be removed.
        if (tooltip !== null) {
          tooltip.remove();
        }
      });
    });
}


/**
 * Initialize the seat management system.
 */
function init_seat_management(selected_ticket_id) {
  init_ticket_selector();

  const tickets = document.querySelectorAll('.ticket');
  if (tickets.length > 0) {
    // Pre-select ticket.
    let ticket_to_preselect;
    if (selected_ticket_id !== null) {
      ticket_to_preselect = find_ticket_by_id(selected_ticket_id);
    } else {
      // Select first ticket by default.
      ticket_to_preselect = tickets[0];
    }
    select_ticket(ticket_to_preselect);

    mark_seats_as_occupiable();
    init_occupiable_seats();
    mark_managed_seats();
    mark_seat_for_selected_managed_ticket();
    wire_seat_release_button();
  }
}


/**
 * Make ticket selector work.
 */
function init_ticket_selector() {
  _make_ticket_selector_open_on_click();
  _select_ticket_on_click();
}


/**
 * Make ticket selector open on click.
 */
function _make_ticket_selector_open_on_click() {
  const ticket_selector = document.querySelector('.ticket-selector');
  if (ticket_selector !== null) {
    ticket_selector.addEventListener('click', function() {
      this.classList.toggle('ticket-selector--open');
    });
  }
}


/**
 * Select ticket on click on ticket in ticket selector.
 */
function _select_ticket_on_click() {
  document.querySelectorAll('.ticket')
    .forEach(function(ticket) {
      ticket.addEventListener('click', function() {
        select_ticket(ticket);
      });
    });
}


/**
 * Return the ticket node in the selector with that ticket ID,
 * or `null` if not found.
 */
function find_ticket_by_id(ticket_id) {
  const ticket = document
    .getElementById('ticket-selection')
    .querySelector('.ticket[data-id="' + ticket_id + '"]');

  if (ticket === null) {
    return null;
  }

  return ticket;
}


/**
 * Set the ticket as the selected one in the ticket selector (both
 * visually and regarding its internal state).
 */
function select_ticket(ticket) {
  const ticket_id = ticket.dataset.id;
  const ticket_code = ticket.dataset.code;

  const ticket_selection = document.getElementById('ticket-selection');
  ticket_selection.dataset.selectedId = ticket_id;
  ticket_selection.dataset.selectedCode = ticket_code;
  ticket_selection.querySelectorAll('.ticket--current')
    .forEach(function(ticket) {
      ticket.classList.remove('ticket--current');
    });

  ticket.classList.add('ticket--current');

  set_current_managed_seat(ticket_id);

  document.getElementById('release-seat-trigger').disabled = !is_ticket_occupying_seat(ticket);
}


function set_current_managed_seat(ticket_id) {
  document.querySelectorAll('.area .seat--managed-current')
    .forEach(function(seat) {
      seat.classList.remove('seat--managed-current');
    });

  document.querySelectorAll('.seat-with-tooltip[data-ticket-id="' + ticket_id + '"] .seat--managed')
    .forEach(function(seat) {
      seat.classList.add('seat--managed-current');
    });
}


function wire_seat_release_button() {
  const release_seat_trigger = document.getElementById('release-seat-trigger');
  if (release_seat_trigger !== null) {
    release_seat_trigger.addEventListener('click', function() {
      const seat_label = get_selected_seat_label();
      const confirmation_label = seat_label + ' (belegt durch Ticket ' + get_selected_ticket_code() + ') freigeben?';
      if (confirm(confirmation_label)) {
        const ticket_id = get_selected_ticket_id();

        const request_url = '/seating/ticket/' + ticket_id + '/seat';

        send_request('DELETE', request_url, function() {
          if (this.readyState === XMLHttpRequest.DONE) {
            if (this.status === 204) {
              reload_with_selected_ticket(ticket_id);
            } else if (this.status === 403 || this.status === 404 || this.status === 500) {
              reload_with_selected_ticket(ticket_id);
            }
          }
        });
      };
      return false;
    });
  }
}


function get_selected_ticket_id() {
  return document.getElementById('ticket-selection').dataset.selectedId;
}


function get_selected_ticket_code() {
  return document.getElementById('ticket-selection').dataset.selectedCode;
}


function is_ticket_occupying_seat(ticket) {
  return ticket.dataset.seatLabel !== undefined;
}


function get_selected_seat_label() {
  const ticket_selection = document.getElementById('ticket-selection');
  const ticket_code = ticket_selection.dataset.selectedCode;
  const ticket = ticket_selection.querySelector('.ticket[data-code="' + ticket_code + '"]');
  return ticket.dataset.seatLabel;
}


function get_managed_ticket_ids() {
  const managed_ticket_ids = new Set();

  document.getElementById('ticket-selection')
    .querySelectorAll('.ticket')
    .forEach(function(ticket) {
      managed_ticket_ids.add(ticket.dataset.id);
    });

  return managed_ticket_ids;
}


function get_seats_with_ticket_code(ticket_id) {
  return document.querySelectorAll('.seat-with-tooltip[data-ticket-id="' + ticket_id + '"] .seat');
}


function mark_managed_seats() {
  const managed_ticket_ids = get_managed_ticket_ids();

  for (const ticket_id of managed_ticket_ids.values()) {
    get_seats_with_ticket_code(ticket_id)
      .forEach(function(seat) {
        seat.classList.add('seat--managed');
      });
  }
}


function mark_seat_for_selected_managed_ticket() {
  const ticket_id = get_selected_ticket_id();
  get_seats_with_ticket_code(ticket_id)
    .forEach(function(seat) {
      seat.classList.add('seat--managed-current');
    });
}


function mark_seats_as_occupiable() {
  document.querySelectorAll('.seat')
    .forEach(function(seat) {
      const ticket_id = seat.parentNode.dataset.ticketId;
      if (ticket_id === undefined) {
        seat.classList.add('seat--occupiable');
      }
    }
  );
}


function init_occupiable_seats() {
  document.querySelectorAll('.seat--occupiable')
    .forEach(function(seat) {
      seat.addEventListener('click', function() {
        const seat_label = seat.parentNode.dataset.label;
        const confirmation_label = seat_label + ' mit Ticket ' + get_selected_ticket_code() + ' reservieren?';
        if (confirm(confirmation_label)) {
          const seat_id = seat.parentNode.dataset.seatId;
          const ticket_id = get_selected_ticket_id();

          const request_url = '/seating/ticket/' + ticket_id + '/seat/' + seat_id;

          send_request('POST', request_url, function() {
            if (this.readyState === XMLHttpRequest.DONE) {
              if (this.status === 204) {
                reload_with_selected_ticket(ticket_id);
              } else if (this.status === 403 || this.status === 404 || this.status === 500) {
                reload_with_selected_ticket(ticket_id);
              }
            }
          });
        };
        return false;
      });
    });
}


function send_request(method, url, state_change_callback) {
  const request = new XMLHttpRequest();
  request.open(method, url);
  request.onreadystatechange = state_change_callback;
  request.send();
}


function reload_with_selected_ticket(ticket_id) {
  location.href = location.href.split('?')[0] + '?ticket=' + ticket_id;
}


/**
 * Use browser's built-in functionality to quickly and safely escape
 * HTML in the given string.
 */
function escape_html(str) {
  const elem = document.createElement('span');
  elem.appendChild(document.createTextNode(str));
  return elem.innerHTML;
}
