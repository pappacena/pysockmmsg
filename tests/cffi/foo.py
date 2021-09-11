from cffi import FFI
ffibuilder = FFI()

ffibuilder.set_source("_example",
   r""" // passed to the real C compiler,
        // contains implementation of things declared in cdef()
        #include <sys/types.h>
        #include <pwd.h>

        // We can also define custom wrappers or other functions
        // here (this is an example only):
        static int get_len(PyObject *bytes) {
            return getpwuid(0);
        }
    """,
    libraries=[])   # or a list of libraries to link with
    # (more arguments like setup.py's Extension class:
    # include_dirs=[..], extra_objects=[..], and so on)

ffibuilder.cdef("""
    // declarations that are shared between Python and C
    #include <sys/types.h>
    #include <sys/socket.h>

    struct passwd *getpwuid(int uid);     // defined in <pwd.h>
    struct passwd *get_pw_for_root(void); // defined in set_source()
""")

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
