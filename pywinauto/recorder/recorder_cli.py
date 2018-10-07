import argparse
import os
import sys
import codecs

if __package__ is None:
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

    from pywinauto.application import Application
    from pywinauto.recorder.uia.uia_recorder import UiaRecorder
else:
    from ..application import Application
    from .uia.uia_recorder import UiaRecorder


def main(args):
    parser = argparse.ArgumentParser(description="Start a recorder")
    app_group = parser.add_mutually_exclusive_group(required=True)
    app_group.add_argument("-c", "--cmd", help="Command line for the application")
    app_group.add_argument("-p", "--process", help="Process ID of application to connect to")
    parser.add_argument("-v", "--verbose", help="Be verbose", action="store_true")
    parser.add_argument("-o", "--out", help="Filename to write generated python script to")
    parser.add_argument("-b", "--backend", choices=["uia"], required=True)
    args = parser.parse_args(args)

    app = Application(backend=args.backend)

    if args.cmd:
        app.start(args.cmd)
    elif args.process:
        app.connect(process=args.process)

    if args.backend == "uia":
        rec = UiaRecorder(app=app, record_props=True, verbose=args.verbose, hot_output=False)
    elif args.backend is None:
        # TODO: auto backend recognition
        raise NotImplementedError()
    else:
        raise Exception("Unsupported backend: '{}'".format(args.backend))

    rec.start()
    rec.wait()

    if args.out:
        with codecs.open(args.out, "w", encoding=sys.getdefaultencoding()) as f:
            f.write(rec.script)
    else:
        print(rec.script)


if __name__ == "__main__":
    main(sys.argv[1:])
