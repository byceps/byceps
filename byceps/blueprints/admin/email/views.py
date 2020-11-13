"""
byceps.blueprints.admin.email.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request, url_for

from ....services.email import service as email_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_success
from ....util.framework.templating import templated
from ....util.views import redirect_to, respond_no_content_with_location

from ...common.authorization.decorators import permission_required
from ...common.authorization.registry import permission_registry

from .authorization import EmailConfigPermission
from .forms import CreateForm, UpdateForm


blueprint = create_blueprint('email_admin', __name__)


permission_registry.register_enum(EmailConfigPermission)


@blueprint.route('/configs')
@permission_required(EmailConfigPermission.view)
@templated
def index():
    """List all e-mail configs."""
    configs = email_service.get_all_configs()

    return {
        'configs': configs,
    }


@blueprint.route('/configs/create')
@permission_required(EmailConfigPermission.create)
@templated
def create_form(erroneous_form=None):
    """Show form to create an e-mail config."""
    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'form': form,
    }


@blueprint.route('/configs', methods=['POST'])
@permission_required(EmailConfigPermission.create)
def create():
    """Create an e-mail config."""
    form = CreateForm(request.form)

    if not form.validate():
        return create_form(form)

    config_id = form.config_id.data.strip()
    sender_address = form.sender_address.data.strip()
    sender_name = form.sender_name.data.strip() or None
    contact_address = form.contact_address.data.strip() or None

    config = email_service.create_config(
        config_id,
        sender_address,
        sender_name=sender_name,
        contact_address=contact_address,
    )

    flash_success(f'Die Konfiguration "{config.id}" wurde angelegt.')
    return redirect_to('.index')


@blueprint.route('/configs/<config_id>/update')
@permission_required(EmailConfigPermission.update)
@templated
def update_form(config_id, erroneous_form=None):
    """Show form to update an e-mail config."""
    config = _get_config_or_404(config_id)

    form = (
        erroneous_form
        if erroneous_form
        else UpdateForm(
            config_id=config.id,
            sender_address=config.sender.address,
            sender_name=config.sender.name,
            contact_address=config.contact_address,
        )
    )

    return {
        'config': config,
        'form': form,
    }


@blueprint.route('/configs/<config_id>', methods=['POST'])
@permission_required(EmailConfigPermission.update)
def update(config_id):
    """Update an e-mail config."""
    config = _get_config_or_404(config_id)

    form = UpdateForm(request.form)
    if not form.validate():
        return update_form(config.id, form)

    sender_address = form.sender_address.data.strip()
    sender_name = form.sender_name.data.strip()
    contact_address = form.contact_address.data.strip()

    config = email_service.update_config(
        config.id, sender_address, sender_name, contact_address
    )

    flash_success(f'Die Konfiguration "{config.id}" wurde aktualisiert.')
    return redirect_to('.index')


@blueprint.route('/configs/<config_id>', methods=['DELETE'])
@permission_required(EmailConfigPermission.delete)
@respond_no_content_with_location
def delete(config_id):
    """Delete an e-mail config."""
    config = _get_config_or_404(config_id)

    success = email_service.delete_config(config.id)

    if success:
        flash_success(f'Die Konfiguration "{config_id}" wurde gelöscht.')
    else:
        flash_error(
            f'Die Konfiguration "{config_id}" konnte nicht gelöscht werden. '
            'Sie scheint noch in Sites verwendet zu werden.'
        )

    return url_for('.index')


def _get_config_or_404(config_id):
    config = email_service.find_config(config_id)

    if config is None:
        abort(404)

    return config
