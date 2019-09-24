(ns dativetop-gui.aol
  (:require [clojure.set :refer [rename-keys]]
            [clojure.string :as str]))

(def has-attr "has")
(def lacks-attr "lacks")
(def is-a-attr "is-a")
(def being-val "being")
(def extant-pred [has-attr, being-val])
(def non-existent-pred [lacks-attr, being-val])
(def being-preds [extant-pred, non-existent-pred])

(defn aol-to-domain-attr-convert
  "Convert an attribute from the AOL-level syntax (which should be more
  human-readable) to the domain-level syntax."
  [quad-attr]
  (if (str/starts-with? quad-attr "has-")
    (->> quad-attr (drop 4) (apply str))
    quad-attr))

(defn appendable->map
  [[[e a v _] _ _]]
  {e (merge
      {:id e}
      (cond
        (some #{[a v]} being-preds) (if (= a has-attr)
                                      {:extant true} {:extant false})
        (= is-a-attr a) {:type v}
        :else {(keyword (aol-to-domain-attr-convert a)) v}))})

(defmulti construct (fn [m] (:type m)))

(defmethod construct "dative-app"
  [m]
  (select-keys m [:id :type :url]))

(defmethod construct "old-service"
  [m]
  (select-keys m [:id :type :url]))

(defmethod construct "old-instance"
  [m]
  (-> m
      (select-keys [:id
                    :type
                    :slug
                    :name
                    :url
                    :leader
                    :state
                    :is-auto-syncing])
      (rename-keys {:is-auto-syncing :auto-sync?})))

(defn aol-to-domain-entities
  "Given an append-only log ``aol`` (a sequence of triples whose first element is
  a <Event, Attribute, Value, Time> quadruple), return a dict from plural domain
  entity type keywords (e.g., ``:old-instances) to sets of domain entity maps."
  [aol]
  (->> aol
       (map appendable->map)
       (apply (partial merge-with merge))
       vals
       (filter :extant)
       (map construct)
       (group-by :type)
       (map (fn [[k v]] [(-> k (str "s") keyword) v]))
       (into {})))


(defn do-the-thing
  [{:keys [target-seen mergee-seen mergee-length index] :as agg}
   [[_ _ target-hash] [_ _ mergee-hash]]]
  (if (or (= target-hash mergee-hash)
          (some #{mergee-hash} target-seen))
    (reduced (assoc agg :ret (- mergee-length index)))
    (let [target-seen (conj target-seen target-hash)
          other-index
          (->> mergee-seen
               reverse
               (filter (fn [[hash _]] (some #{hash} target-seen)))
               first
               second)]
      (if other-index
        (reduced (assoc agg :ret (- mergee-length other-index)))
        (merge agg
               {:target-seen target-seen
                :mergee-seen (conj mergee-seen [mergee-hash index])
                :index (inc index)})))))

(defn find-changes
  [target mergee]
  (if-not (seq target)  ;;  target is empty, all of mergee is new
    mergee
    (let [{:keys [ret]}
          (reduce
           do-the-thing
           {:target-seen []  ;; suffix of target hashes seen
            :mergee-seen []  ;; suffix of mergee hashes seen (2-vecs with indices)
            :mergee-length (count mergee)
            :index 0
            :ret nil}
           (->> [(reverse target) (reverse mergee)]
                (apply interleave)
                (partition 2)))]
      (if ret (drop ret mergee) mergee))))

(defn merge-aols
  "Merge AOL ``mergee`` into AOL ``target``.

  Parameter ``target`` (coll) is the AOL that will receive the changes.
  Parameter ``mergee`` (coll) is the AOL that will be merged into target; the
  AOL that provides the changes.
  Keyword parameter conflict-resolution-strategy (keyword) describes how to
  handle conflicts. If the strategy is 'rebase', we will append the new quads
  from ``mergee`` onto ``target``, despite the fact that this will result in
  hashes for those appended quads that differ from their input hashes in
  ``mergee``.
  Keyword parameter ``diff-only`` (boolean) will, when true, result in a return
  value consisting simply of the suffix of the merged result that ``mergee``
  would need to append to itself in order to become identical with ``target``;
  when false, we return the entire modified ``target``.
  Always returns a 2-tuple maybe-type structure."
  [target mergee
   & {:keys [conflict-resolution-strategy diff-only]
      :or {conflict-resolution-strategy :abort
           diff-only false}}]
  :stuff)
