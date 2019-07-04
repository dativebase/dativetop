(ns dativetop-gui.main)

(def value-a 4)

(defonce value-b 2)

(defn reload! []
  (println "Code updated. andr Mozzzzznkeys")
  (println "Trying values:" value-a value-b))

(defn main! []
  (println "App loaded with mucho gusto!"))
