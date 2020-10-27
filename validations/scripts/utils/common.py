#
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#

import logging
import subprocess
import paramiko
import time
from messages.user_messages import *
from cortx.utils.security.cipher import Cipher, CipherInvalidToken

logger = logging.getLogger(__name__)


def run_subprocess_cmd(cmd, **kwargs):
    _kwargs = dict(
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    _kwargs.update(kwargs)
    _kwargs['check'] = True

    if not _kwargs.get('timeout', None):
        _kwargs['timeout'] = 15
    if isinstance(cmd, str):
        cmd = cmd.split()

    try:
        logger.debug(f"Subprocess command {cmd}, kwargs: {_kwargs}")
        res = subprocess.run(cmd, **_kwargs)
    except subprocess.TimeoutExpired as exc:
        result = (1, str(exc), repr(exc))
        logger.error(f"Subprocess command resulted in: {result}")
    except Exception as exc:
        result = (1, str(exc), repr(exc))
        logger.error(f"Subprocess command resulted in: {result}")
    else:
        logger.debug(f"Subprocess command resulted in: {res}")
        result = (res.returncode, res.stdout, res.stderr)
    return result


def ssh_remote_machine(hostname, username=None, password=None, port=22):
    # cmd = "pip3 install paramiko"
    # run_subprocess_cmd(cmd)
    # time.sleep(5)
    ssh_client = paramiko.client.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #ssh_client=paramiko.SSHClient(paramiko.AutoAddPolicy())

    response = {}
    message = ""
    try:
        ssh_client.connect(hostname, port, username, password)
        stdin, stdout, stderr = ssh_client.exec_command(
            'hostname', bufsize=-1, timeout=None, get_pty=False)
        result = stdout.readlines()
        # ssh_client.close()
        logger.debug(f"Response: {result}, Error: {stderr.readlines()}")

        response['ret_code'] = 0
        response['response'] = stdout
        response['error_msg'] = stderr
        response['message'] = result
    except Exception as exc:
        message = str(SSH_CONN_EXCEPTION).format(hostname, exc)
        logger.error(message)
        response['ret_code'] = 1
        response['response'] = str(exc)
        response['error_msg'] = repr(exc)
        response['message'] = message

    ssh_client.close()
    return  response


def decrypt_secret(enc_key, secret):
    """ Decrypt secret value.
    """
    logger.debug("Decrypt secret value.")
    response = {}
    try:
        response['response'] = "{0}".format((Cipher.decrypt(enc_key, secret.encode("utf-8"))).decode("utf-8"))
        response['message'] = str(DECRYPT_PASSWD_SUCCESS)
    except CipherInvalidToken:
        # Already decrypted, nothing to do
        response['message'] = str(DECRYPT_PASSWD_FAILED).format(secret)
        response['response'] = secret

    return response
