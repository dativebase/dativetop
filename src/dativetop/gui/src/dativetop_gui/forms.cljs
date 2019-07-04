;; View functions for DativeTop GUI forms

;; .. note:: These are **not** web forms, i.e., collections of text and select
;;    inputs. These are **linguistic** forms, i.e., words, morphemes, phrases,
;;    sentences, etc.

;; Functions that return re-com widget components which react (i.e., modify the
;; DOM, or subscribe) to events emitted by the app database and which trigger
;; events based on a user's interaction with the GUI.
(ns dativetop-gui.forms
  (:require [re-com.core   :refer [h-box v-box box gap line title label
                                   hyperlink input-text input-password
                                   button p single-dropdown]]
            [reagent.core :as reagent]
            [re-frame.core :as re-frame]
            [clojure.string :as string]
            [cljs.pprint :refer [pprint]]
            [dativetop-gui.utils  :refer [panel-title title2 RHS-column-style
                                   center-gap-px zip split-into-words
                                   split-into-morphemes get-word-id]]
            [dativetop-gui.subs   :as subs]
            [goog.string :as gstring]
            [goog.string.format]))

;; ============================================================================
;; Add a new form functionality
;; ============================================================================

(defn forms-add-panel
  []
  [v-box
   :children [[panel-title "Create a new form"]
              [gap :size "10px"]
              [p "This is where the use will be able to create a new OLD
                 form."]]])

;; ============================================================================
;; Form IGT display functionality
;; ============================================================================

;; Constants (or user-modifiable settings?)
;; ============================================================================

;; These are the IGT attributes of forms (those that should be aligned into
;; word-width columns.
(def igt-attrs [:transcription
                :morpheme-break
                :morpheme-gloss])

(def max-igt-line-len 40)  ;; the maximum length in characters of an IGT line
(def min-igt-line-len 20)  ;; the minimum length in characters of an IGT line
(def igt-line-step 3)      ;; the distance (in characters) that each subsequent
                           ;; IGT line is left- indented

;; Functions
;; ============================================================================

(defn get-igt-vals
  "Given a form map, return a map of just its IGT fields as defined by
  igt-attrs."
  [form]
  (into {} (map (fn [attr] [attr (attr form)]) igt-attrs)))

(defn split-into-words-morphemes
  "Given a map from form attributes to strings, return a map to vectors of
  vectors, where each inner vector contains one or more morphemes and zero or
  more morpheme delimiters. E.g.,
  {:transcription  les chiens
   :morpheme-break le-s chien=s
   :morpheme-gloss DET-PL dog=PL}
  becomes
  {:transcription  [[les] [chiens]]
   :morpheme-break [[le - s] [chien = s]]
   :morpheme-gloss [[DET - PL] [dog = PL]]}"
  [form-igt-fields]
  (into {}
        (map (fn [[attr phrase]]
               [attr
                (into []
                      (map split-into-morphemes (split-into-words phrase)))])
               form-igt-fields)))

(defn pad-word-lists
  "Given a map whose values are word lists containing morpheme vectors,
  e.g., (([les]) ([le - s] [chien - s])),
  append empty vectors to the shorter word lists so that all are the same
  length, e.g.,
  e.g., (([les] []) ([le - s] [chien - s]))."
  [igt-vals]
  (let [word-count (apply max (map count (vals igt-vals)))]
    (into {}
          (map (fn [[attr igt-line]]
                 (let [line-count (count igt-line)]
                   [attr
                    (if (> word-count line-count)
                      (concat igt-line (take (- word-count line-count)
                                             (repeat [])))
                      igt-line)]))
               igt-vals))))

(defn get-longest-word-length
  "For each word list containing words of the same column,
  e.g., ([les] [le - s] [DET - PL]),
  return the character length of the longest word, e.g., 6."
  [word-list]
  (->> word-list
       (map (fn [morph-list]
              (reduce + (map (fn [morph] (count morph)) morph-list))))
       (apply max)))

(defn get-longest-word-lengths
  "Given a list of lists of words in the same IGT column, return a list of
  lengths corresponding to the longest word in each column. Needed for
  specifying box (i.e., column) widths."
  [igt-struct]
  (map (fn [word-list]
         (get-longest-word-length word-list))
       igt-struct))

(defn split-word-lengths-into-lines
  "Given a list of word lengths, returns a vector of maps each representing an
  IGT line with a left-side indent and a vector of longest word lengths (a
  subvector of the input list), e.g., 
  [{:indent 0, :word-lens [6 7 13 7 5]}
   {:indent 6, :word-lens [3 5 4 12 6]}"
  [word-lens]
  (let [tmp
        (reduce
          (fn [ret word-len]
            (let [current-word-lens (:current-line ret)
                  proposed-word-lens (conj current-word-lens word-len)
                  proposal-len (reduce + proposed-word-lens)
                  max-line-len (:max-line-len ret)]
              (if (< proposal-len max-line-len)
                (assoc ret :current-line proposed-word-lens)
                (let [new-max-line-len (- max-line-len igt-line-step)
                      new-max-line-len (if (< new-max-line-len min-igt-line-len)
                                         min-igt-line-len new-max-line-len)
                      current-lines (:lines ret)
                      indent (- max-igt-line-len max-line-len)]
                  (if (= 1 (count proposed-word-lens))
                    {:current-line []
                     :max-line-len new-max-line-len
                     :lines
                     (conj current-lines {:indent indent
                                          :word-lens proposed-word-lens})}
                    {:current-line [word-len]
                     :max-line-len new-max-line-len
                     :lines
                     (conj current-lines {:indent indent
                                          :word-lens current-word-lens})})))))
            {:current-line []
             :max-line-len max-igt-line-len
             :lines []}
            word-lens)
        last-current-line (:current-line tmp)
        lines (:lines tmp)]
    (if (seq last-current-line)
      (conj lines {:indent (- max-igt-line-len (:max-line-len tmp))
                   :word-lens last-current-line})
      lines)))

(defn add-offsets
  "Takes a vector of line metadata maps like:
  [{:indent 0, :word-lens [6 7 13 7 5]}
   {:indent 6, :word-lens [3 5 4 12 6]}]
  and adds offsets:
  [{:indent 0, :word-lens [6 7 13 7 5] :offset 0}
   {:indent 6, :word-lens [3 5 4 12 6] :offset 5}]"
  [lines-metadata]
  (->> lines-metadata
       (reduce-kv (fn [ret idx {word-lens :word-lens :as line-metadata}]
                    (let [last-offset (:last-offset ret)
                          new-offset (+ last-offset (count word-lens))
                          new-line-metadata (assoc line-metadata :offset
                                                   last-offset)
                          existing-lines-metadata (:lines-metadata ret)
                          new-lines-metadata (conj existing-lines-metadata
                                                   new-line-metadata)]
                      (-> ret
                          (assoc :last-offset new-offset)
                          (assoc :lines-metadata new-lines-metadata))))
                  {:last-offset 0 :lines-metadata []})
       :lines-metadata))

(defn build-igt-lines
  "Takes an IGT map like
  {:transcription ([les] [chiens] [dormient] [pendant] [que] [la] [ville] [se] [brule] [les]),
   :morpheme-break ([le - s] [chien - s] [dorm - ient] [pendant] [que] [la] [ville] [se] [brul - e] [le - s]),
   :morpheme-gloss ([DET - PL] [dog - PL] [sleep - 3PL.PRS] [while] [COMPL] [DET] [city] [REFL] [fire - 3SG.PRS] [DET - PL])}
  and a vector of IGT line metadata
  [{:indent 0, :word-lens [6 7 13 7 5], :offset 0}
   {:indent 6, :word-lens [3 5 4 12 6], :offset 5}
  and returns a vector of IGT line metadata where the appropriate words are in
  the appropriate line, e.g.
  [{:indent 0, :word-lens [6 7 13 7 5], :offset 0 :attr :transcription
    :words ([les] [chiens] [dormient] [pendant] [que])}
   {:indent 0, :word-lens [6 7 13 7 5], :offset 0 :attr :morpheme-break
    :words ([le - s] [chien - s] [dorm - ient] [pendant] [que])}
   ...
   {:indent 6, :word-lens [3 5 4 12 6], :offset 5 :attr :transcription
    :words ([la] [ville] [se] [brule] [le])}
   ...]"
  [igt-map igt-lines-metadata]
  (reduce
    (fn [ret-vec {offset :offset word-lens :word-lens :as meta}]
      (let [line-group
            (map (fn [igt-attr]
                   (let [all-words (into [] (igt-attr igt-map))]
                     (-> meta
                         (assoc :attr igt-attr)
                         (assoc :words
                                (subvec
                                  all-words offset (+ offset (count word-lens)))))))
                 igt-attrs)]
        (concat ret-vec line-group)))
    []
    igt-lines-metadata))

(defn get-igt-lines
  "Returns a vector of IGT line maps, given an igt-map from form IGT attributes
  to vectors of word vectors ({:transcription [[s]], :morpheme-break ...}),
  and a vector of lines metadata, e.g., [{:indent 0, :word-lens [2]} {...]."
  [igt-map igt-lines-metadata]
  (->> igt-lines-metadata
       add-offsets
       (build-igt-lines igt-map)))

(defn compute-igt-lines
  "Given an OLD linguistic form, return a map representing an ordered sequence
  of IGT lines (in the :igt-lines attr of that map). Each IGT line has the
  following:
  - words: vector of vectors of morphemes and delimiters, e.g., [[le - s]
      [ville - s]].
  - indent: the size of the left-hand indent in characters.
  - word-lens: vector of maximum word lengths for each word in words. This
      determines the column width of each word column, e.g., [5 7].
  - offset: the offset of the first word of the line within the entire value,
      e.g., if the phrase is `le-s chien-s sont fatigu-é-s` and the line at hand
      is `sont fatigue-é-s`, then the offset will be 2 because `sont` is the
      third word.
  - attr: the form attribute being displayed, e.g., :morpheme-break."
  [form]
  (let [igt-map (-> form
                    get-igt-vals
                    split-into-words-morphemes
                    pad-word-lists)]
    (->> (vals igt-map)
         (apply zip)
         get-longest-word-lengths
         split-word-lengths-into-lines
         (get-igt-lines igt-map))))

(defn get-match-message
  [type_ manner id modifier relatee category]
  (gstring/format
    "This %s %s matches the form with id %s, %s as \"%s\", having category
    \"%s\"." type_ manner id modifier relatee category))

(defn igt-char
  "Display a character in an IGT word. Each character can register a dbl-click
  event which transitions the form to ``edit mode`` and places the cursor on
  the dbl-clicked character."
  [chr form attr line-idx word-idx char-idx]
  [:span
   {:on-double-click
    #(re-frame/dispatch
       [:igt-char-double-clicked (:id form) attr line-idx word-idx char-idx])}
   chr])

(defn string->vec-igt-chars
  "Given a string token (representing word word-idx of IGT line line-idx of
  attribute attr of form form), return a vector of character <span>s as
  returned by igt-char; char-offset indicates how far (in chars) the word is
  from the start of the entire attr value. These <span>s trigger editable mode
  when double-clicked."
  [token form attr line-idx word-idx abs-word-idx char-offset]
  (into []
        (map-indexed
          (fn [char-idx chr]
            (igt-char chr form attr line-idx word-idx
                      (+ char-offset char-idx)))
          token)))

(defn perfect-hlink
  "Return the morpheme or gloss token as a re-com hyperlink to the perfect-match
  vector. Example inputs:
  token: s
  attr: :morpheme-break
  perfect-match: [4 [PL Num]]"
  [token attr perfect-match form line-idx word-idx abs-word-idx char-offset]
  [hyperlink
   :label [h-box
           :children (string->vec-igt-chars token form attr line-idx word-idx
                                            abs-word-idx char-offset)]
   :style {:color :blue}
   :tooltip (let [[id [relatee category]] perfect-match
                  [type_ modifier]
                  (if (= attr :morpheme-break)
                    ["morpheme" "glossed"] ["gloss" "transcribed"])]
              (get-match-message
                type_ "exactly" id modifier relatee category))])

(defn partial-hlink
  "Return the morpheme or gloss token as a re-com hyperlink to the partial
  matches map my-refs. Example inputs:
  token: s
  attr: :morpheme-break
  partial-matches: {3 [plural number] 4 [PL Num]}"
  [token attr partial-matches form line-idx word-idx abs-word-idx char-offset]
  (let [[type_ modifier]
        (if (= attr :morpheme-break)
          ["morpheme" "glossed"] ["gloss" "transcribed"])
        msgs
        (map (fn [[id [relatee category]]]
               (get-match-message
                 type_ "partially" id modifier relatee category))
             partial-matches)]
    [hyperlink
     :label [h-box
             :children (string->vec-igt-chars token form attr line-idx word-idx
                                              abs-word-idx char-offset)]
     :style {:color :green}
     :tooltip (string/join " " msgs)]))

(defn morpheme-link
  "Given token (a morpheme or a gloss) return a blue link to its exact match
  morpheme form entry, or else a green link to its partial match, or else just
  the token (no matches)."
  [form attr token my-refs their-refs line-idx word-idx abs-word-idx char-offset]
  (if (seq my-refs)
    (let [my-refs (into {} (map (fn [[id ctrprt cat]] [id [ctrprt cat]])
                                my-refs))
          their-refs (if (seq their-refs)
                       (into {} (map (fn [[id ctrprt cat]] [id [ctrprt cat]])
                                     their-refs)) {})
          perfect-match (->> my-refs
                             (filter
                               (fn [[id _]]
                                 (if (get their-refs id) true false)))
                             first)]
      (if perfect-match
        ;; FOXFUCK
        (perfect-hlink token attr perfect-match form line-idx word-idx
                       abs-word-idx char-offset)
        (partial-hlink token attr my-refs form line-idx word-idx abs-word-idx
                       char-offset)))
    [h-box
     :children (string->vec-igt-chars token form attr line-idx word-idx
                                      abs-word-idx char-offset)]))

(defn get-morph-idx->char-offset
  "Given a vector of morphemes, e.g., [un - break - able], return a map from
  morpheme indices to character indices, in this case
  {0 0, 1 2, 2 3, 3 8, 4 9}."
  [morph-list]
  (dissoc
    (reduce-kv
      (fn [{last-offset :last-offset :as ret} morph-idx morph]
        (let [new-offset (+ last-offset (count morph))]
          (-> ret
              (assoc morph-idx last-offset)
              (assoc :last-offset new-offset))))
      {:last-offset 0}
      morph-list)
    :last-offset))

(defn morpheme-links
  "Converts a vector of morphemes/glosses and delimiters to a hiccup data
  structure where morphemes may be hyperlinks to their matching lexical entries
  in the database, if there are any such matches."
  [morph-list abs-word-idx form line-idx word-idx attr]
  (let [_ (println "morpheme-break-ids")
        _ (println (:id form))
        _ (println (:morpheme-break-ids form))
        _ (println (:morpheme-gloss-ids form))
        break-refs (nth (:morpheme-break-ids form) abs-word-idx)
        gloss-refs (nth (:morpheme-gloss-ids form) abs-word-idx)
        [mine theirs] (if (= attr :morpheme-break)
                        [break-refs gloss-refs]
                        [gloss-refs break-refs])
        morph-idx->char-offset (get-morph-idx->char-offset morph-list)]
    (into []
          (map-indexed
            (fn [morph-idx token]
              (let [char-offset (morph-idx->char-offset morph-idx)]
                (if (even? morph-idx)  ;; even = morphs/glosses; odd = delims
                  (let [ref-idx (/ morph-idx 2)]
                    (morpheme-link form attr token (nth mine ref-idx)
                                   (nth theirs ref-idx) line-idx word-idx
                                   abs-word-idx char-offset))
                  (igt-char token form attr line-idx word-idx char-offset))))
            morph-list))))

(def word-input-meta-keys
  ["Escape"  ;; should exit edit mode
   "Backspace"  ;; should join the current word to the previous one
   " "  ;; should cause the focused word to be incremented ...
   "ArrowUp"  ;; should move to the word above
   "ArrowDown"  ;; should move to the word below
   ])

(defn key-up-form-word-edit-input
  [e form-id attr line-idx word-idx abs-word-idx igt-line]
  (let [key (.-key e)]
    (when (some #{key} word-input-meta-keys)
      (case key
        " " (re-frame/dispatch [:split-word-at (-> e .-target .-selectionStart)
                                form-id attr line-idx word-idx abs-word-idx igt-line])
        "Escape" (re-frame/dispatch [:switch-to-display-mode form-id])))))

(defn word-edit-input
  "Display a text input for editing a single word of an IGT form line."
  [morph-list form width line-idx word-idx offset attr igt-line]
  (let [word-id (get-word-id (:id form) attr (+ offset word-idx))
        [foc-attr foc-line-idx foc-word-idx foc-char-idx :as focused-word]
        (get-in form [:dativetop-gui-metadata :focused-word])]
    (reagent/create-class
      {:component-did-mount
       (fn []
         (let [input-id (get-word-id (:id form) foc-attr (+ offset foc-word-idx))
               ; _ (println input-id)
               input (.getElementById js/document input-id)
               ; _ (println input)
               ]
           ; (println "got here")
           (when input (.focus input))


         ;(println "word edit input DID MOUNT " morph-list)
         ;(when (= (list attr line-idx word-idx) (take 3 focused-word))
           ;(let [inp (.getElementById js/document word-id)
                 ;char-idx (last focused-word)
                 ;_ (println "word " morph-list " should be focused")
                 ;]
             ;(.focus inp)
             ;(.setSelectionRange inp char-idx char-idx))))

             ))
       :reagent-render
       (fn [morph-list form width line-idx word-idx offset attr igt-line]
         ; (println "word edit input RENDERED with morph-list " morph-list)
         [input-text
          ;; FOX
          :validation-regex #"^[^\s]*$"
          :attr {:id word-id
                 :on-key-up
                 (fn [e] (key-up-form-word-edit-input
                           e (:id form) attr line-idx word-idx
                           (+ offset word-idx) igt-line))}
          :width width
          :style {:padding "3px 4px"
                  :line-height "1.9em"
                  :height "24px"}
          :model (string/join "" morph-list)
          :change-on-blur? false
          :on-change (fn [new-value]
                        (re-frame/dispatch
                          [:igt-input-changed new-value (:id form) attr
                           line-idx word-idx (+ offset word-idx)]))])})))

(defn igt-word-display
  "Display a single IGT word (possibly multi-morphemic) without any
  cross-referencing links to other forms."
  [morph-list form line-idx word-idx attr]
  (into []
        (map-indexed
          (fn [char-idx chr]
            (igt-char chr form attr line-idx word-idx char-idx))
          (flatten (map seq morph-list)))))

(defn word-box
  "Takes a word as a vector of morphemes and delimiters (morph-list), the index
  of the IGT line, the index of the word within the line, the offset of the
  word within the entire IGT form value, the (longest) word length, the form
  itself, and the attribute (e.g., :morpheme-break) on display in this line,
  and returns a re-com h-box for displaying that word with a calculated width
  (which will equal that of all of the other words in the same column) and with
  morpheme cross-references as links, if applicable."
  [morph-list line-idx word-idx offset word-length form attr igt-line]
  (let [width (str (* 0.8 word-length) "em")]
    ; (println "word-box rendered " morph-list)
    [h-box
     :children (cond
                 (= :edit (get-in form [:dativetop-gui-metadata :state]))
                 [[word-edit-input morph-list form width line-idx word-idx
                   offset attr igt-line]]
                 (some #{attr} [:morpheme-break :morpheme-gloss])
                 (morpheme-links morph-list (+ offset word-idx) form line-idx
                                 word-idx attr)
                 :else
                 (igt-word-display morph-list form line-idx word-idx attr))
     :width width]))

(defn char-len->ems
  "Convert a number of characters to a string approximating how long an average
  string of that length would be in em units."
  [char-len]
  (str (* 0.8 char-len) "em"))

(defn igt-line-indent
  "Return a div to create a left-hand IGT indent, with a width based on the
  supplied character length."
  [char-len]
  [:div {:style {:width (char-len->ems char-len)}}])

(defn igt-line-box
  "Return a re-com h-box that displays an IGT line: a (possibly zero-length
  indent div followed by one or more word-boxes."
  [igt-line line-idx form]
  [h-box
   :gap "5px"
   :children
   (concat [(igt-line-indent (:indent igt-line))]
           (into []
                 (map-indexed
                   (fn [word-idx morph-list]
                     [word-box morph-list
                               line-idx
                               word-idx
                               (:offset igt-line)
                               (nth (:word-lens igt-line) word-idx)
                               form
                               (:attr igt-line)
                               igt-line])
                   (:words igt-line))))])

(defn igt
  "Return a re-com v-box containing the IGT (interlinear glossed text) values
  of the form. These are the values that are aligned by words into columns."
  [form]
  (let [igt-lines (compute-igt-lines form)]
    [v-box
     :gap "5px"
     :children
     (into []
           (map-indexed
             (fn [line-idx igt-line]
               [igt-line-box igt-line line-idx form])
             igt-lines))]))

(defn form-view
  "Display a linguistic form."
  [form]
  (let [index (inc (get-in form [:dativetop-gui-metadata :index]))]
    [h-box
     :gap "10px"
     :children
     [(str index ".")
      [igt form]]]))

(defn forms-browse-panel
  "Display all visible linguistic forms."
  []
  (let [visible-forms @(re-frame/subscribe [:visible-forms])]
    [v-box
     :children [[panel-title "Forms"]
                [gap :size "20px"]
                [v-box
                 :gap "20px"
                 :children
                 (into []
                       (for [[id form] visible-forms]
                         ^{:key id}
                         [form-view form]))]]]))

(defn add-panel
  "Display the form for creating a new OLD linguistic form."
  []
  [forms-add-panel])

(defn browse-panel [] [forms-browse-panel])
