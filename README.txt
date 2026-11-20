# TonyOS dev — multi-slot OS lab (/lab)
# Machine: Lenovo ideacentre AIO 510-23ASR (personal-lenovo-aio)

Partitions on /dev/sda:
  sda1 (2G FAT32)  EFI-LAB      -> /boot/efi (UEFI ESP, GRUB + custom .efi kernels)
  sda2 (60G ext4)  RESCUE-HOST  -> /         (Default Ubuntu 24.04 LTS base, zero snapd)
  sda3 (80G ext4)  SLOT-A       -> unmounted (OS Experiment Slot A)
  sda4 (80G ext4)  SLOT-B       -> unmounted (OS Experiment Slot B)
  sda5 (8G swap)   SWAP-SHARED  -> swap      (Shared swap + zram zstd 50%)
  sda6 (~701G)     LAB-DATA     -> /lab      (Shared repos, images, logs)

Safe one-shot boot commands (auto-fallback to RESCUE-HOST on hard reboot):
  sudo grub-reboot "<GRUB menu entry>" && sudo reboot
  sudo efibootmgr --bootnext <XXXX> && sudo reboot
