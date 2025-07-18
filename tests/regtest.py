import os
import sys
import unittest
import subprocess
from typing import Mapping, Any


class TestLightning(unittest.TestCase):
    agents: Mapping[str, Mapping[str, Any]]

    @staticmethod
    def run_shell(args, timeout=30):
        process = subprocess.Popen(['tests/regtest/regtest.sh'] + args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, universal_newlines=True)
        for line in iter(process.stdout.readline, ''):
            sys.stdout.write(line)
            sys.stdout.flush()
        process.wait(timeout=timeout)
        process.stdout.close()
        assert process.returncode == 0

    def setUp(self):
        test_name = self.id().split('.')[-1]
        sys.stdout.write("***** %s ******\n" % test_name)
        # initialize and get funds
        for agent, config_options in self.agents.items():
            self.run_shell(['init', agent])
            for k, v in config_options.items():
                self.run_shell(['setconfig', agent, k, v])
        # mine a block so that funds are confirmed
        self.run_shell(['new_block'])
        # start daemons
        for agent in self.agents:
            self.run_shell(['start', agent])

    def tearDown(self):
        for agent in self.agents:
            self.run_shell(['stop', agent])


class TestUnixSockets(TestLightning):
    agents = {}

    def test_unixsockets(self):
        self.run_shell(['unixsockets'])


class TestLightningAB(TestLightning):
    agents = {
        'alice': {
            'test_force_disable_mpp': 'false',
            'test_force_mpp': 'true',
        },
        'bob': {
            'lightning_listen': 'localhost:9735',
        }
    }

    def test_collaborative_close(self):
        self.run_shell(['collaborative_close'])

    def test_backup(self):
        self.run_shell(['backup'])

    def test_backup_local_forceclose(self):
        self.run_shell(['backup_local_forceclose'])

    def test_breach(self):
        self.run_shell(['breach'])

    def test_extract_preimage(self):
        self.run_shell(['extract_preimage'])

    def test_redeem_received_htlcs(self):
        self.run_shell(['redeem_received_htlcs'])

    def test_redeem_offered_htlcs(self):
        self.run_shell(['redeem_offered_htlcs'])

    def test_breach_with_unspent_htlc(self):
        self.run_shell(['breach_with_unspent_htlc'])

    def test_breach_with_spent_htlc(self):
        self.run_shell(['breach_with_spent_htlc'])

    def test_lnwatcher_waits_until_fees_go_down(self):
        self.run_shell(['lnwatcher_waits_until_fees_go_down'])


class TestLightningSwapserver(TestLightning):
    agents = {
        'alice': {
            'use_gossip': 'false',
            'swapserver_url': 'http://localhost:5455',
            'nostr_relays': "''",
        },
        'bob': {
            'lightning_listen': 'localhost:9735',
            'plugins.swapserver.enabled': 'true',
            'plugins.swapserver.port': '5455',
            'nostr_relays': "''",
        }
    }

    def test_swapserver_success(self):
        self.run_shell(['swapserver_success'])

    def test_swapserver_forceclose(self):
        self.run_shell(['swapserver_forceclose'])

    def test_swapserver_refund(self):
        self.run_shell(['swapserver_refund'])



class TestLightningWatchtower(TestLightning):
    agents = {
        'alice': {
        },
        'bob': {
            'lightning_listen': 'localhost:9735',
            'watchtower_url': 'http://wtuser:wtpassword@127.0.0.1:12345',
        },
        'carol': {
            'plugins.watchtower.enabled': 'true',
            'plugins.watchtower.server_user': 'wtuser',
            'plugins.watchtower.server_password': 'wtpassword',
            'plugins.watchtower.server_port': '12345',
        }
    }

    def test_watchtower(self):
        self.run_shell(['watchtower'])


class TestLightningABC(TestLightning):
    agents = {
        'alice': {
        },
        'bob': {
            'lightning_listen': 'localhost:9735',
            'lightning_forward_payments': 'true',
        },
        'carol': {
        }
    }

    def test_fw_fail_htlc(self):
        self.run_shell(['fw_fail_htlc'])


class TestLightningJIT(TestLightning):
    agents = {
        'alice': {
            'accept_zeroconf_channels': 'true',
        },
        'bob': {
            'lightning_listen': 'localhost:9735',
            'lightning_forward_payments': 'true',
            'accept_zeroconf_channels': 'true',
        },
        'carol': {
        }
    }

    def test_just_in_time(self):
        self.run_shell(['just_in_time'])


class TestLightningJITTrampoline(TestLightningJIT):
    agents = {
        'alice': {
            'use_gossip': 'false',
            'accept_zeroconf_channels': 'true',
        },
        'bob': {
            'lightning_listen': 'localhost:9735',
            'lightning_forward_payments': 'true',
            'lightning_forward_trampoline_payments': 'true',
            'accept_zeroconf_channels': 'true',
        },
        'carol': {
            'use_gossip': 'false',
        }
    }
