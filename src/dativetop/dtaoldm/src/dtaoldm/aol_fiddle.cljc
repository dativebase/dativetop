(ns dtaoldm.aol-fiddle
  (:require [clojure.string :as str]
            [me.raynes.fs :as fs]
            [dtaoldm.aol :as aol]
            [dtaoldm.utils :as u]))

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

(defrecord A [x y])

(defrecord B [a b c d e f g h i j k l m n o p])

(comment

  (->B 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15)

  (vals (->B 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15))


  (let [x (->A 1 2)
        b (assoc x :z "zzz")]
    [x (type x) b (type b)])

  (->A 1 2)

  (get (->A 1 2) :y)

  (vals (->A 1 2))

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

  (aol/serialize-quad [1 2 3])

  (aol/get-hash-of-quad [1 2 3])

  (aol/get-hash-of-quad [{"a" 2 "b" {"c" [1 2 3]}} 1 2 3])

  (u/get-uuid)

  (aol/fiat-entity)

  (let [[entity-id & _ :as exist] (aol/fiat-entity)]
    [exist
     (aol/fiat-attribute entity-id "likes" "chocolate")])

  (let [x (when-not true :f)] x)

  (aol/domain-to-aol-attr-convert :cool)

  (map (fn [x] x) {:a 2 :b 3})

  (aol/instance-to-quads {:id "abc" :a 2} "dog")

  (aol/fiat-entity "abc")

  (aol/fiat-entity)

  (aol/fiat-attribute "abc" aol/is-a-attr "dog")

  (name :abc-d)

  (name "abc-d")

  (aol/get-tip-hash [[] [1 2]])

  (aol/get-tip-hash [[] []])

  (aol/get-tip-hash [])

  (let [instance {:id "abc"
                  :url "http://localhost:8087/old"}
        quads (aol/instance-to-quads instance "old-service")]
    (str/join (map aol/serialize-appendable quads))
  )

  (conj [1 2] 3)

  (let [instance {:id "abc"
                  :url "http://localhost:8087/old"}
        quads (aol/instance-to-quads instance "old-service")
        aol (reduce aol/append-to-aol [] quads)]
    (aol/write-aol-to-file aol "blargon5.txt"))

  (-> "a\nb\n"
      str/split-lines
      )

  (aol/get-tip-hash-in-file "blargon5.txt")

  (aol/get-tip-hash-in-file "blargon6.txt")

  (let [aol [[["abc" "has" "being" "2019-10-03T19:32:15.354000"]
              "42fffcf403277400df19049f92c967bf"
              "4b9f78a556a1952e6930c8cbaf3373b0"]
             [["abc" "is-a" "old-service" "2019-10-03T19:32:15.354000"]
              "67c3e80f468f203ee7e94a9dd1e728ed"
              "afb5d9f7113c8c0bc980824251412fbf"]
             [["abc" "has-id" "abc" "2019-10-03T19:32:15.355000"]
              "a2d3dff5f46ed617f2f844f743fc7cba"
              "027461962d2602e1a329a434d5ffbd5c"]
             [["abc" "has-url" "http://localhost:8087/old" "2019-10-03T19:32:15.355000"]
              "0109ea56c3445e4d3ec9f02477436936"
              "f79ed7936afa7c25290582039cff6fe1"]]]

    #_(aol/get-new-appendables aol nil)
    #_(aol/get-new-appendables aol "4b9f78a556a1952e6930c8cbaf3373b0")
    (aol/get-new-appendables aol "f79ed7936afa7c25290582039cff6fe1")
    #_(= (aol/get-new-appendables aol "4b9f78a556a1952e6930c8cbaf3373b0")
       (aol/get-new-appendables aol nil))
    #_(aol/get-new-appendables aol "afb5d9f7113c8c0bc980824251412fbf")
    )

  (conj [1 2] 3)

  (cons 1 [2 3])

  ;; Show that persist-aol (append-aol-to-file) is idempotent (repeated
  ;; application has no effect)
  (let [aol [[["abc" "has" "being" "2019-10-03T19:32:15.354000"]
              "42fffcf403277400df19049f92c967bf"
              "4b9f78a556a1952e6930c8cbaf3373b0"]
             [["abc" "is-a" "old-service" "2019-10-03T19:32:15.354000"]
              "67c3e80f468f203ee7e94a9dd1e728ed"
              "afb5d9f7113c8c0bc980824251412fbf"]
             [["abc" "has-id" "abc" "2019-10-03T19:32:15.355000"]
              "a2d3dff5f46ed617f2f844f743fc7cba"
              "027461962d2602e1a329a434d5ffbd5c"]
             [["abc" "has-url" "http://localhost:8087/old" "2019-10-03T19:32:15.355000"]
              "0109ea56c3445e4d3ec9f02477436936"
              "f79ed7936afa7c25290582039cff6fe1"]]
        ]
    (doseq [i (range (count aol))]
      (aol/append-aol-to-file (take (inc i) aol) "aol-1.txt"))
    (doseq [i (range 100)]
      (aol/persist-aol aol "aol-2.txt"))
    (aol/persist-aol aol "aol-3.txt")
    (= (slurp "aol-1.txt")
       (slurp "aol-2.txt")
       (slurp "aol-3.txt")))

  (fs/touch "dogs")

  (fs/file? "adogs")

  (-> "aol-1.txt"
      aol/read-aol
      aol/aol-to-domain-entities)

  (let [aol [[["abc" "has" "being" "2019-10-03T19:32:15.354000"]
              "42fffcf403277400df19049f92c967bf"
              "4b9f78a556a1952e6930c8cbaf3373b0"]
             [["abc" "is-a" "old-service" "2019-10-03T19:32:15.354000"]
              "67c3e80f468f203ee7e94a9dd1e728ed"
              "afb5d9f7113c8c0bc980824251412fbf"]
             [["abc" "has-id" "abc" "2019-10-03T19:32:15.355000"]
              "a2d3dff5f46ed617f2f844f743fc7cba"
              "027461962d2602e1a329a434d5ffbd5c"]
             [["abc" "has-url" "http://localhost:8087/old" "2019-10-03T19:32:15.355000"]
              "0109ea56c3445e4d3ec9f02477436936"
              "f79ed7936afa7c25290582039cff6fe1"]]
        ]
    (aol/aol-valid? aol))

  (-> "aol-1.txt"
      aol/read-aol
      aol/aol-valid?)

  (take 3 (repeat nil))

  (every? true? [true true true])

)
