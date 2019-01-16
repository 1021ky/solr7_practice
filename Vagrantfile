# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"

  config.vm.provider :virtualbox do |vb|
    vb.customize ["setextradata", :id, "VBoxInternal/Devices/VMMDev/0/Config/GetHostTimeDisabled", 0]
  end

  DEV_HOSTNAME = "dev"
  config.vm.define DEV_HOSTNAME do |machine|
    machine.vm.hostname = DEV_HOSTNAME
    machine.vm.synced_folder ".", "/vagrant"

    machine.vm.network "forwarded_port", guest: 8983, host: 8983

    machine.vm.provider "virtualbox" do |vb|
      vb.memory = "2056"
      vb.cpus=2
    end
    
    machine.vm.provision :ansible_local do |ansible|
      ansible.inventory_path = "playbook/inventory/hosts"
      ansible.playbook       = "playbook/playbook.yml"
      ansible.install_mode   = :pip
      ansible.version        = "2.4.0.0" # needs to set install_mode :pip
      ansible.verbose        = true
    end
  end
end
