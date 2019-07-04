(ns server.main)

(def value-a 1)

(defonce value-b 2)

(defn mach [v]
  (* v 8))

(defn reload! []
  (println "Code updated and again.")
  (println "GOX Trying values:" value-a value-b))

(defn main! []
  (println "Appz loaded!"))
