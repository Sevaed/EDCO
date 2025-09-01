from . import tui


def test_configuration_to_groups():

    configuration = {
        "EDCO": {
            "path": "/home/seva/.config/EDCO.json"
        },
        "config_not_need_anymore": {
            "path": "/home/seva/.config/scripts/config.py"
        },
        "hyprland": {
            "path": "/home/seva/.config/hypr/hyprland.conf",
            "group": "hyprland",
            "command": [
                "hyprctl",
                "reload"
            ]
        },
        "keybindings": {
            "path": "/home/seva/.config/hypr/custom/keybindings.conf",
            "group": "hyprland"
        },
        "autostart": {
            "path": "/home/seva/.config/hypr/custom/autostart.conf",
            "group": "hyprland"
        },
        "windowrule": {
            "path": "/home/seva/.config/hypr/custom/windowrule.conf",
            "group": "hyprland"
        },
        "hypr-base": {
            "path": "/home/seva/.config/hypr/rices/base.conf",
            "group": "hyprland"
        },
        "hypr-solya": {
            "path": "/home/seva/.config/hypr/rices/solya.conf",
            "group": "hyprland"
        },
        "waybar": {
            "path": "/home/seva/.config/waybar/config",
            "group": "waybar",
            "command": [
                "pkill",
                "-SIGUSR1",
                "waybar"
            ]
        },
        "waybar-css": {
            "path": "/home/seva/.config/waybar/style.css",
            "group": "waybar"
        },
        "kitty": {
            "path": "/home/seva/.config/kitty/kitty.conf",
            "group": "terminal",
            "command": [
                "sh",
                "-c",
                "kill -SIGUSR1 $(pgrep kitty)"
            ]
        },
        "fish": {
            "path": "/home/seva/.config/fish/config.fish",
            "group": "terminal",
            "command": [
                "fish",
                "-c",
                "source ~/.config/fish/config.fish"
            ]
        },
        "nvim": {
            "path": "/home/seva/.config/nvim/init.lua",
            "group": "nvim"
        },
        "nvim_lsp": {
            "path": "/home/seva/.config/nvim/lua/lsp.lua",
            "group": "nvim"
        },
        "nvim_options": {
            "path": "/home/seva/.config/nvim/lua/options.lua",
            "group": "nvim"
        },
        "nvim_plugins": {
            "path": "/home/seva/.config/nvim/lua/plugins.lua",
            "group": "nvim"
        },
        "tmux": {
            "path": "/home/seva/.config/.tmux.conf"
        }
    }

    groups = tui.configuration_to_groups(configuration)

    assert groups == {'hyprland': ['keybindings', 'windowrule', 'hypr-solya', 'autostart', 'hypr-base', 'hyprland'], 'nvim': ['nvim_options', 'nvim_plugins',
                                                                                                                              'nvim_lsp', 'nvim'], 'waybar': ['waybar-css', 'waybar'],
                      'terminal': ['kitty', 'fish'], None: ['config_not_need_anymore', 'EDCO', 'tmux']}


def test_calculate_menu():
    blocks = []
    current_choice = [0, 0]
    groupss = {'waybar': ['waybar', 'waybar-css'], None: ['EDCO']}
    test_data1, test_data2 = tui.calculate_menu(
        blocks, current_choice, groupss)
    itog1 = [(2, 2, "▼ waybar", 1), (2, 16, "▼ nogroup", 3)]
    itog2 = [(3, 2, "├── waybar", "reverse"),
             (4, 2, "└── waybar-css", "2"), (3, 16, "└── EDCO", "4")]
    assert test_data1 == itog1
    assert test_data2 == itog2
