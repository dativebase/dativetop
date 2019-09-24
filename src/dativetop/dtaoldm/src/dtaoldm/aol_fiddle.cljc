(ns dtaoldm.aol-fiddle
  (:require [clojure.string :as str]
            [dtaoldm.aol :as aol]))

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

  (let [tests
        [[[]
          [[0 0 :a] [0 0 :b] [0 0 :c]]
          [[0 0 :a] [0 0 :b] [0 0 :c]]]
         [[]
          [[0 0 :a] [0 0 :b] [0 0 :c] [0 0 :X]]
          [[0 0 :a] [0 0 :b] [0 0 :c]]]
         [[[0 0 :d]]
          [[0 0 :a] [0 0 :b] [0 0 :c]]
          [[0 0 :a] [0 0 :b] [0 0 :c] [0 0 :d]]]
         [[[0 0 :d]]
          [[0 0 :a] [0 0 :b] [0 0 :c] [0 0 :X]]
          [[0 0 :a] [0 0 :b] [0 0 :c] [0 0 :d]]]
         [[[0 0 :d]]
          [[0 0 :a] [0 0 :b] [0 0 :c] [0 0 :X] [0 0 :Y]]
          [[0 0 :a] [0 0 :b] [0 0 :c] [0 0 :d]]]
         [[[0 0 :d] [0 0 :e]]
          [[0 0 :a] [0 0 :b] [0 0 :c] [0 0 :X]]
          [[0 0 :a] [0 0 :b] [0 0 :c] [0 0 :d] [0 0 :e]]]
         [[]
          []
          []]
         [[]
          [[0 0 :a]]
          [[0 0 :a]]]
         [[[0 0 :d]]
          []
          [[0 0 :d]]]
         [[[0 0 :d]]
          [[0 0 :X]]
          [[0 0 :d]]]
         [[[0 0 :d]]
          [[0 0 :X] [0 0 :Y]]
          [[0 0 :d]]]
         [[[0 0 :d] [0 0 :e]]
          [[0 0 :X]]
          [[0 0 :d] [0 0 :e]]]]]
    (every?
     identity
     (map
      (fn [[expected arg1 arg2]]
        (= expected (aol/find-changes arg1 arg2)))
      tests)))

  (aol/get-hash "joel")

  (= "c000ccf225950aac2a082a59ac5e57ff"
     (aol/get-hash "joel"))

  (aol/get-json {"dog" 2 "cat" 0})

  (-> {"dog" 2 "cat" 0}
      aol/get-json
      aol/parse-json)

  (aol/get-now)

  (aol/get-now-str)

)
