# Fish‐completion for `config` (репозиторий edco-config-manager)

function __fish_config_list_names
    # подавляем ошибки при отсутствии имени
    config --_list-names ^/dev/null
end

# Опции
complete -c config -l p      -d "Print path to config"
complete -c config -l c      -d "Print contents of config"
complete -c config -l a      -d "Add new config"
complete -c config -l n      -d "Show all configs"
complete -c config -l d      -d "Delete config(s)"
complete -c config -l h      -d "Show help message"
complete -c config -l install-completion -d "Install shell completions"
# Автодополнение имён из JSON
complete -c config -f -a "(__fish_config_list_names)"

