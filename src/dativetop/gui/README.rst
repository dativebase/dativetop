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

    $ yarn shadow-cljs watch dativetop-gui

Open a CS REPL to the process::

    $ yarn shadow-cljs cljs-repl dativetop-gui

Do the above two steps with Make and tmux::

    $ make run-repl

Build a production release::

    $ npx shadow-cljs release dativetop-gui


Connect to Shadow-CLJS nREPL with Spacemacs and Cider
================================================================================

1. Start the app and connect to the REPL from the command line using the make
   rule given above::

       $ make run-repl

   With the above, there should be an nREPL at localhost:8082.

2. Navigate to DativeTop in a browser at http://127.0.0.1:8081/.

3. In Spacemacs, run `C-m C-s C-c` (or `C-c M-c` ... what you want is
   `cider-connect-cljs` and at the prompts select `localhost` and `8082`.

4. In Spacemacs, open the Cider REPL buffer; find it with `Space b b` and
   execute the following::

       shadow.user> (shadow.cljs.devtools.api/nrepl-select :dativetop-gui)


Documentation notes
=============================================================================

DativeTop is an application for linguistic data management.

It lets you manage Online Linguistic Database (OLD) instances on your local
machine and configure them to sync with leader OLDs on the web.

DativeTop lets you use the Dative graphical user interface to work with your
OLD instances.

To view Dative, click the "View" menu item and then "Dative". Click the
"Help" menu item and then "Visit Dative in Browser" to open Dative in
your web browser.

Online Linguistic Database Instances

These are your local Online Linguistic Database instances.

You may have to manually tell Dative about these OLD instances by adding new
"server" instances for them under Dative > Application Settings.
