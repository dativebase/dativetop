(ns dativetop-gui.aol-fiddle
  (:require [clojure.string :as str]
            [dativetop-gui.aol :as aol]
            [goog.string :as gstring]
            [goog.string.format :as format]))

(def test-aol
  (list
   [["d5265c65-fc1b-4b74-bc96-b9e4c08f4874"
     "has"
     "being"
     "2019-09-23T17:29:01.623453"]
    "fdf93a9485cc6fa332588d6af46ac6f4"
    "ed1d168f2c45ce1ad624a8755cc49ee2"]
   [["d5265c65-fc1b-4b74-bc96-b9e4c08f4874"
     "is-a"
     "dative-app"
     "2019-09-23T17:29:01.623478"]
    "59d604fc67114e745da4a5fd8eb58411"
    "d3351a1932a6832ffcc39ee17a5661f2"]))

(comment

  (aol/aol-to-domain-attr-convert "has-cat")

  (aol/aol-to-domain-attr-convert "is-cat")

  (let [[[e a v t] h ih] [["thing" "is" "blue" "now"] "abc" "def"]]
    (gstring/format "The %s %s %s at time %s. Hash: %s. Integrated hash %s"
            e a v t h ih))

  aol/aol-to-domain-entities

  (let [test-aol (list
                  [["d5265c65-fc1b-4b74-bc96-b9e4c08f4874"
                    "has"
                    "being"
                    "2019-09-23T17:29:01.623453"]
                   "fdf93a9485cc6fa332588d6af46ac6f4"
                   "ed1d168f2c45ce1ad624a8755cc49ee2"]
                  [["d5265c65-fc1b-4b74-bc96-b9e4c08f4874"
                    "is-a"
                    "dative-app"
                    "2019-09-23T17:29:01.623478"]
                   "59d604fc67114e745da4a5fd8eb58411"
                   "d3351a1932a6832ffcc39ee17a5661f2"])]
    (aol/aol-to-domain-entities test-aol))

  (def target-abc [[nil nil :a] [nil nil :b] [nil nil :c]])
  (def target-abcX [[nil nil :a] [nil nil :b] [nil nil :c] [nil nil :X]])

  (= () (aol/find-changes target-abc target-abc))

  (* 8 8)

)
