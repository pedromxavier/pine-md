from cstream import stdout, stderr

def repl(globals: dict, locals: dict) -> None:
    try:
        while True:
            try:
                _in = input(">>> ")
                if not _in:
                    break
                try:
                    stdout[0] << eval(_in, globals, locals)
                except:
                    out = exec(_in, globals, locals)
                    if out != None:
                        stdout[0] << out
            except Exception as e:
                stderr[0]<< f"Error: {e}"
    except KeyboardInterrupt as e:
        print("\nExiting...")