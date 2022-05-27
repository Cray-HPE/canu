from fakenos import FakeNOS

inventory = {
    "hosts": {
        "router1": {
            "port": 6005,
            "nos": {"plugin": "MyFakeNOSPlugin"} # (1)
        }
    }
}

net = FakeNOS(inventory)

net.register_nos_plugin(plugin="my_nos.yaml") # (2)

net.start()    