PLUGIN_DASHBOARD_DIR=$(cd $(dirname $BASH_SOURCE)/.. && pwd)
PLUGIN_ENABLED_DIR=$PLUGIN_DASHBOARD_DIR/myplugin/enabled
OPENSTACK_DASHBOARD_DIR=$DEST/horizon/openstack_dashboard
HORIZON_ENABLED_DIR=$OPENSTACK_DASHBOARD_DIR/local/enabled

function install_plugin {
    setup_develop $PLUGIN_DASHBOARD_DIR
}

function configure_plugin {
    cp -a $PLUGIN_ENABLED_DIR $HORIZON_ENABLED_DIR
}

if is_service_enabled my-plugin; then

    if [[ "$1" == "stack" && "$2" == "pre-install"  ]]; then
        :

    elif [[ "$1" == "stack" && "$2" == "install"  ]]; then
        echo_summary "Installing My Plugin"
        install_plugin

    elif [[ "$1" == "stack" && "$2" == "post-config"  ]]; then
        echo_summary "Configurng My Plugin"
        configure_plugin

    elif [[ "$1" == "stack" && "$2" == "extra"  ]]; then
        :
    fi

    if [[ "$1" == "unstack"  ]]; then
        :
    fi

    if [[ "$1" == "clean"  ]]; then
        :
    fi
fi
