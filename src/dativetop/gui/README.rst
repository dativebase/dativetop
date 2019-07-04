================================================================================
  DativeTop ClojureScript GUI
================================================================================

It displays a web-based (HTML, Clojure/Java-Script) interface to locally served
DativeTop desktop application.

Install shadow-cljs using npm::

    $ npm install -g shadow-cljs

Install dependencies and setup basic scaffolding::

    $ yarn
    $ mkdir -p target && cp assets/index.html target/

Run in development::

    $ yarn shadow-cljs watch app

Open a CS REPL to the process::

    $ yarn shadow-cljs cljs-repl app

Do the above two steps with Make and tmux::

    $ make run-repl

