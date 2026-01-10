"""
    secrets index
"""

import zoom
import zoom.fields as f
import zoom.request
import zoom.validators as v

from zoom.encryption import generate_key, get_encryption_key
from zoom.secrets import Secret, get_secrets_store

class SecretField(f.MemoField):
    """Secret Field"""

    def show(self):
        return ''

    def display_value(self):
        return '*' * len(self.value)


def secret_fields():
    result = f.Fields(
        f.TextField('Name', v.required),
        f.MemoField('Description', v.required),
        SecretField('Value', v.required, browse=False, editable=False),
        f.DateField('Expiry', hint='optional'),
    )
    if zoom.system.request.route[-1] == 'edit':
        del result.fields[2]
    return result


class SecretsView(zoom.collect.CollectionView):

    def new_key(self, *a, **k):

        key_exists = get_secrets_key()
        if key_exists:
            message = """
            <h3>Configuration Complete</h3>
            This site already has a site key available for
            encyrption. You can enable the Secrets feature
            """
        else:
            message = """
            <h3>Configuration Required</h3>
            This site does not currently have a site key available for
            encyrption. You can replace the key
            """

        return zoom.page(
            message +
            ' by saving the key in '
            'the file named /run/secrets/zoom_secrets_key (recommended) or by '
            'providing the key in an environment variable named ZOOM_SECRETS_KEY.'
            '<br><br>'
            'If your secrets are file based (recommended) but stored elsewhere you can use'
            ' the evironment variable ZOOM_SECRETS_PATH to tell zoom where to look for the'
            ' secrets files.'
            '<br><br>'
            'Here is a new key if you need one: %s' % generate_key().decode(),
            title='New Key',
        )


main = zoom.collection_of(
    secret_fields,
    store=get_secrets_store(),
    model=Secret,
    view=SecretsView,
    url='/secrets'
)
