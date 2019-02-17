import argparse
import codecs
import os
import sys

from six import PY3

if PY3:
    import configparser
else:
    import ConfigParser as configparser

if __package__ is None:
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

    from pywinauto.application import Application
    from pywinauto.recorder.uia.uia_recorder import UiaRecorder
    from pywinauto.recorder.win32.win32_recorder import Win32Recorder
    from pywinauto.recorder.recorder_config import RecorderConfig
else:
    from ..application import Application
    from .uia.uia_recorder import UiaRecorder
    from .recorder_config import RecorderConfig


def main(argv):
    backend_choises = ["uia", "win32"]

    conf_parser = argparse.ArgumentParser(add_help=False)
    conf_parser.add_argument("-c", "--config", help="Specify config file")
    args, remaining_argv = conf_parser.parse_known_args(argv)

    config_options = {}

    if args.config:
        config = configparser.ConfigParser()
        config.read([args.config])
        config_options = dict(config.items("Config"))
        for key in ["verbose", "key_only", "scale_click"]:
            if key in config_options:
                config_options[key] = config.getboolean("Config", key)

    parser = argparse.ArgumentParser(parents=[conf_parser])
    parser.set_defaults(**config_options)
    app_group = parser.add_mutually_exclusive_group()
    app_group.add_argument("-l", "--cmd", help="Command line for the application")
    app_group.add_argument("-p", "--process", help="Process ID of application to connect to")
    parser.add_argument("-v", "--verbose", help="Be verbose", action="store_true")
    parser.add_argument("-o", "--out", help="Filename to write generated python script to")
    parser.add_argument("-b", "--backend", help="Which backend to use", choices=backend_choises)
    parser.add_argument("-k", "--key_only", help="Access items only by key (app['Window Title'])", action="store_true")
    parser.add_argument("-s", "--scale_click", action="store_true",
                        help="Use scaled relative click coordinates when calling 'click_input()' method")
    args = parser.parse_args(remaining_argv)

    config = RecorderConfig()
    config.apply(**vars(args))

    if config.backend not in backend_choises:
        parser.error("backend must be specified. Choices: {{{}}}".format(", ".join(backend_choises)))

    if not config.cmd and not config.process:
        parser.error("either cmd or process must be specified")

    app = Application(backend=config.backend)

    if config.cmd:
        app.start(config.cmd)
    else:
        app.connect(process=config.process)

    if config.backend == "uia":
        rec = UiaRecorder(app=app, config=config)
    elif config.backend == "win32":
        rec = Win32Recorder(app=app, config=config)
    elif config.backend is None:
        # TODO: auto backend recognition
        raise NotImplementedError()
    else:
        raise Exception("Unsupported backend: '{}'".format(config.backend))

    rec.start()
    rec.wait()

    if config.out:
        with codecs.open(config.out, "w", encoding=sys.getdefaultencoding()) as f:
            f.write(rec.script)
    else:
        print(rec.script)


if __name__ == "__main__":
    main(sys.argv[1:])
