Welcome to bindpyrame's documentation!
======================================

Basic usage
-----------
This module provides a class and a function to call pyrame's module (for more info about pyrame see http://llr.in2p3.fr/sites/pyrame/)  without creating a pyrame module.

For example, to use the function **onearg**  with argument **test_onearg**  of the **cmd_test** module which is  listening on port **localhost:9007** we can use the following approaches.

The function way
________________

The use of the sendcmd function is::

       import bindpyrame


       bindpyrame.sendcmd("localhost",9007,"onearg_test","test_onearg")
       => (1, u'onearg(test_onearg)')

One has to note that the function of pyrame's module should be the complete name that is containing _ and module name (here onearg_test)


The class way
_____________

The usage of the class is::

     import bindpyrame

     # connect to the module running at port 9007 here cmd_test
     p = bindpyrame.PyrameProxy('localhost',9007)
     p.onearg("test_onearg")
     =>  (1, u'onearg(test_onearg)')


     # print_list_function() is a method to show the prototype of the the available functions from the module
     p.print_list_functions()
     => available functions are:

        cmod_resolve(  )
        apipools(  )
        wakemeup(  )
        void(  )
        init( dev_name, arg1, arg2, arg3 )
        asyncwait( time )
        infargs(  )
        onearg( arg1 )
        getmyfile(  )
        getmyport(  )
        varmod(  )
        twoargs( arg1, arg2 )
        newns( ns )
        fail(  )
        getvar( name )
        gettestport(  )
        setvar( ns, name, value )
        pool(  )

Here the name of the pyrame'module function is a method of the class.

Some details
------------
The fact that the module get the name of the function is because of the overriding of the **__getattr__** of the class to catch the exception.


Table of contents
=================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


   modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
