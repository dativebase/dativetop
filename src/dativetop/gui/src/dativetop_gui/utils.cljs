(ns dativetop-gui.utils
  (:require [re-com.core :refer [h-box v-box box gap title line label
                                 hyperlink-href align-style]]
            [camel-snake-kebab.core :refer [->kebab-case]]
            [clojure.string :as string]
            [cljs-time.core :as cljs-time]))


; narrow, light grey column of text, on the RHS
(def RHS-column-style
  {:style {:width "450px"
           :font-size "13px"
           :color "#aaa"}})


;; the gap betwen the the two columns
(def center-gap-px "100px")


(defn dativetop-gui-title-box
  []
  [h-box
   :justify :center
   :align   :center
   :height  "62px"
   :style   {:background-color "#666"}
   :children [[title
               :label "Dative"
               :level :level1
               :style {:font-size   "32px"
                       :color       "#fefefe"}]]])

(defn github-hyperlink
  "given a label and a relative path, return a component which hyperlinks to the GitHub URL in a new tab"
  [label src-path]
  (let [base-url (str "https://github.com/Day8/re-com/tree/master/")]
    [hyperlink-href
     :label  label
     ;:style  {:font-size    "13px"}
     :href   (str base-url src-path)
     :target "_blank"]))

(defn panel-title
  "Shown across the top of each page"
  [panel-name src1 src2]
  [v-box
   :children [[h-box
               :margin "0px 0px 9px 0px"
               :height "54px"
               :align :end
               :children [[title
                           :label         panel-name
                           :level         :level1
                           :margin-bottom "0px"
                           :margin-top    "2px"]
                          [gap :size "25px"]
                          (when src1 [h-box
                                      :class "all-small-caps"
                                      :gap    "7px"
                                      :align  :center
                                      :children [
                                                 [label :label "source:" ]
                                                 [github-hyperlink "component" src1]
                                                 [label :label "|"  :style {:font-size "12px"}]
                                                 ;[line]
                                                 [github-hyperlink "page" src2]]])]]
              [line]]])

(defn title2
  "2nd level title"
  [text style]
  [title
   :label text
   :level :level2
   :style style])

(defn status-text
  "given some status text, return a component that displays that status"
  [status style]
  [:span
   [:span.bold "Status: "]
   [:span {:style style} status]])

(defn material-design-hyperlink
  [text]
  [hyperlink-href
   :label  text
   :href   "http://zavoloklom.github.io/material-design-iconic-font/icons.html"
   :target "_blank"])



(defn arg-row
  "I show one argument in an args table."
  [name-width arg odd-row?]
  (let [required   (:required arg)
        default    (:default arg)
        arg-type   (:type arg)
        needed-vec (if (not required)
                     (if (nil? default)
                       [[:span.semibold.all-small-caps "optional"]]
                       [[:span.semibold.all-small-caps "default:"] [:span.semibold (str default)]])
                     [[:span.semibold.all-small-caps "required"]])]
    [h-box
     :style    {:background (if odd-row? "#F4F4F4" "#FCFCFC")}
     :children [[:span {:class "semibold"
                        :style (merge (align-style :align-self :center)
                                      {:width        name-width
                                       :padding-left "15px"})}
                 (str (:name arg))]
                [line :size "1px" :color "white"]
                [v-box
                 :style {:padding "7px 15px 2px 15px"}
                 :gap  "4px"
                 :width "310px"
                 :children [[h-box
                             :gap   "4px"
                             :children (concat [[:span.semibold  arg-type]
                                                [gap :size "10px"]]
                                               needed-vec)]
                            [:p
                              {:font-size "smaller" :color "red"}
                              (:description arg)]]]]]))


(defn args-table
  "I display a component arguements in an easy to read format"
  [args]
  (let [name-width  "130px"]
    (fn
      []
      [v-box
       :children (concat
                   [[title2 "Parameters"]
                    [gap :size "10px"]]
                   (map (partial arg-row name-width)  args (cycle [true false])))])))


(defn scroll-to-top
  [element]
  (set! (.-scrollTop element) 0))


(defn get-current-old-instance-url
  [old-instances current-old-instance]
  (:url (get old-instances current-old-instance)))


(defn ->kebab-case-recursive
  "Converts
  {:cow_bird [{:frog_face 2}] :dog_fish {:cat_bird 2}}
  to
  {:cow-bird [{:frog-face 2}] :dog-fish {:cat-bird 2}}"
  [data-structure]
  (cond
    (map? data-structure)
    (into {}
          (map (fn [[k v]]
                 [(if (keyword? k) (->kebab-case k) k)
                  (->kebab-case-recursive v)])
               data-structure))
    (sequential? data-structure)
    (into (if (vector? data-structure) [] '())
          (map (fn [el] (->kebab-case-recursive el)) data-structure))
    :else
    data-structure))

(defn get-now [] (cljs-time/now))

(defn get-index
  "Return an absolute index within an entire (server-stored) collection."
  [idx page items-per-page]
  (+ idx (* (dec page) items-per-page)))

(defn add-dativetop-gui-metadata
  "For each map in coll add the timestamp of when it was retrieved and its
  absolute index within the entire (server-stored) collection."
  [now page items-per-page coll]
  (map-indexed
    (fn [idx item]
      (assoc item
             :dativetop-gui-metadata
             {:retrieved now
              :index (get-index idx page items-per-page)
              :state :display}))
    coll))

(defn zip [& colls] (partition (count colls) (apply interleave colls)))

;; TODO: these should be taken from the OLD instance's app settings.
(def morpheme-delimiter #"([-=])")  ;; Morphemes are split on hyphens or equals signs

(defn split-into-words [word] (string/split word #"\s+"))
(defn join-into-phrase [word-coll] (string/join " " word-coll))

(defn split-into-morphemes
  [morpheme]
  (string/split morpheme morpheme-delimiter))

(defn get-word-id
  [form-id attr abs-word-idx]
  (string/join "-" ["form" form-id "attr" (name attr) "word" abs-word-idx]))
