import binascii
import base64
import string


class ENMBase64:
    @staticmethod
    def is_base64(resource: string):
        try:
            if isinstance(resource, str):
                resource_bytes = bytes(resource, 'ascii')
            elif isinstance(resource, bytes):
                resource_bytes = resource
            else:
                raise ValueError("Argument must be string or bytes")
            return base64.b64encode(base64.b64decode(resource_bytes)) == resource_bytes
        except binascii.Error:
            return False
        except UnicodeDecodeError:
            return False

    def decode_base64(self, resource: string):
        resource_state = self.is_base64(resource)
        convert_resource = ''
        if resource_state:
            convert_resource = base64.b64decode(resource).decode('ascii')
        return resource_state, convert_resource