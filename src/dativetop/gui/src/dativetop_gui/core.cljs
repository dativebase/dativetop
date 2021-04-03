(ns dativetop-gui.core
  (:require [reagent.core :as reagent]
            [ajax.core :as ajax]
            [clojure.pprint :as pprint]
            [day8.re-frame.http-fx]
            [re-frame.core :as rf]
            [re-com.core
             :refer
             [h-box v-box box gap line scroller border label p title alert-box
              row-button button h-split checkbox]
             :refer-macros [handler-fn]]
            [re-com.util :refer [enumerate]]
            [clojure.string :as str]
            [goog.string :as gstring]
            [goog.string.format]
            [dativetop-gui.aol :as aol]
            [dativetop-gui.aol-fiddle :as aol-fiddle]))

;; -- Helpers & Data -----------------------------------------------------------

(def default-db
  {:dativetop-server {:url "http://127.0.0.1:4676"}
   :dative-app {:url "http://127.0.0.1:0000"}
   :old-service {:url "http://127.0.0.1:1111"}
   :olds []
   :new-old {:name "" :short-name "" :leader ""}})

(defn new-old-valid?
  [new-old]
  false)

(def col-widths
  {:name "7.5em"
   :url "15em"
   :leader "20em"
   :state "8em"
   :auto-sync? "8em"
   :actions "7em"})

(defmulti url (fn [resource & _] resource))

;; GET: fetch the OLD service
;; PUT: update the URL of the OLD service
(defmethod url :old-service [_ dtserver-url] (str dtserver-url "/old_service"))

;; GET: fetch the Dative app
;; PUT: update the URL of the Dative app
(defmethod url :dative-app [_ dtserver-url] (str dtserver-url "/dative_app"))

;; GET: fetch all of the OLDs
;; POST: create a new OLD
(defmethod url :olds [_ dtserver-url] (str dtserver-url "/olds"))

;; GET: fetch a specific OLD
;; PUT: update an OLD
;; DELETE: delete an OLD
(defmethod url :old [_ dtserver-url old-id] (str dtserver-url "/olds/" old-id))

;; PUT: transition an OLD's state
(defmethod url :old-state [_ dtserver-url old-id]
  (str dtserver-url "/olds/" old-id "/state"))

;; POST: enqueue a new command
;; PUT: pop the next command off of the queue
(defmethod url :sync-old-commands [_ dtserver-url]
  (str dtserver-url "/sync_old_commands"))

;; GET: fetch a specific command
;; DELETE: complete a command
(defmethod url :sync-old-command [_ dtserver-url command-id]
  (str dtserver-url "/sync_old_commands/" command-id))

(comment

  (let [dtserver-url "http://127.0.0.1:4567"
        id "123"]
    [(url :old-service dtserver-url)
     (url :dative-app dtserver-url)
     (url :olds dtserver-url)
     (url :old dtserver-url id)
     (url :old-state dtserver-url id)
     (url :sync-old-commands dtserver-url)
     (url :sync-old-command dtserver-url id)])

)

;; -- Domino 1 - Event Dispatch -----------------------------------------------

;; -- Domino 2 - Event Handlers -----------------------------------------------

(rf/reg-event-db :init (fn [_ _] default-db))

(rf/reg-event-fx
 :fetch-old-service
 (fn [{{{dtserver-url :url} :dativetop-server :as db} :db} _]
   {:db db
    :http-xhrio
    {:method :get
     :headers {:Content-Type "application/json; utf8"}
     :format :json
     :uri (url :old-service dtserver-url)
     :timeout 8000
     :response-format (ajax/json-response-format {:keywords? true})
     :on-success [:fetch-old-service-success]
     :on-failure [:fetch-old-service-failure]}}))

(rf/reg-event-db
 :fetch-old-service-success
 (fn [db [_ old-service]] (assoc db :old-service old-service)))

(rf/reg-event-db
 :fetch-old-service-failure
 (fn [db [_ old-service]]
   (print "fetch OLD service failure with ...")
   (print old-service)
   db))

(rf/reg-event-fx
 :fetch-dative-app
 (fn [{{{dtserver-url :url} :dativetop-server :as db} :db} _]
   {:db db
    :http-xhrio
    {:method :get
     :headers {:Content-Type "application/json; utf8"}
     :format :json
     :uri (url :dative-app dtserver-url)
     :timeout 8000
     :response-format (ajax/json-response-format {:keywords? true})
     :on-success [:fetch-dative-app-success]
     :on-failure [:fetch-dative-app-failure]}}))

(rf/reg-event-db
 :fetch-dative-app-success
 (fn [db [_ dative-app]] (assoc db :dative-app dative-app)))

(rf/reg-event-db
 :fetch-dative-app-failure
 (fn [db [_ dative-app]]
   (print "fetch Dative app failure with ...")
   (print dative-app)
   db))

;; -- Domino 4 - Query  -------------------------------------------------------

(rf/reg-sub
 :old-service-url
 (fn [db _]
   (-> db :old-service :url)))

(rf/reg-sub
 :dative-app-url
 (fn [db _]
   (-> db :dative-app :url)))

;; -- Domino 5 - View Functions ----------------------------------------------

(defn data-row
  [row first? last?]
  [h-box
   :class "rc-div-table-row"
   :children
   [[label
     :label (:name row)
     :width (:name col-widths)]
    [label
     :label (:url row)
     :width (:url col-widths)]
    [h-box
     :gap      "2px"
     :width    (:actions col-widths)
     :align    :center
     :children
     [[row-button
       :md-icon-name    "zmdi zmdi-copy"
       :tooltip         "Copy this line"
       ;:mouse-over-row? mouse-over-row?
       ;:on-click        #(reset! click-msg (str "copy row " (:id row)))
       ]
      [row-button
       :md-icon-name    "zmdi zmdi-edit"
       :tooltip         "Edit this line"
       ;:mouse-over-row? mouse-over-row?
       ;:on-click        #(reset! click-msg (str "edit row " (:id row)))
       ]
      [row-button
       :md-icon-name    "zmdi zmdi-delete"
       :tooltip         "Delete this line"
       ;:mouse-over-row? mouse-over-row?
       ;:on-click        #(reset! click-msg (str "delete row " (:id row)))
       ]]]]])

(defn data-table
  [rows]
  (let [mouse-over (reagent/atom nil)
        click-msg  (reagent/atom "")]
    (fn []
      [v-box
       :class "rc-div-table"
       :children
       [[h-box
         :class    "rc-div-table-header"
         :children [[label :label "Name" :width (:name col-widths)]
                    [label :label "URL" :width (:url col-widths)]
                    [label :label "Actions" :width (:actions col-widths)]]]
        (for [[_ row first? last?] (enumerate (sort-by :sort (vals rows)))]
          ^{:key (:url row)} [data-row row first? last?])]])))

(defn format-old-instance-row
  [old-instance]
  ^{:key (:url old-instance)}
  [:tr.old-instance
   [:td (:name old-instance)]
   [:td (:url old-instance)]
   [:td (get old-instance :leader "")]
   [:td ""]])

(defn old-instances-gui-header
  []
  [h-box
   :class "rc-div-table-header"
   :children
   [[label
     :label "Name"
     :width (:name col-widths)]
    [label
     :label "URL"
     :width (:url col-widths)]
    [label
     :label "Leader"
     :width (:leader col-widths)]
    [label
     :label "State"
     :width (:state col-widths)]
    [label
     :label "Auto-sync?"
     :width (:auto-sync? col-widths)]
    [label
     :label "Actions"
     :width (:actions col-widths)]
    ]])

(defn old-instances-gui-row
  [old-instance mouse-over]
  (let [mouse-over-row? (identical? @mouse-over old-instance)]
    [h-box
     :class "rc-div-table-row"
     :attr {:on-mouse-over (handler-fn (reset! mouse-over old-instance))
            :on-mouse-out  (handler-fn (reset! mouse-over nil))}
     :children
     [[label
       :label (:name old-instance)
       :width (:name col-widths)]
      [label
       :label (:url old-instance)
       :width (:url col-widths)]
      [scroller
       :h-scroll :auto
       :width (:leader col-widths)
       :child
       [label
        :label (get old-instance :leader "")]]
      [label
       :label (get old-instance :state)
       :width (:state col-widths)]
      [box
       :width (:auto-sync? col-widths)
       :child
       [checkbox
        :model (:auto-sync? old-instance)
        :on-change
        #(rf/dispatch [:auto-sync?-changed (:url old-instance) %])]]
      [h-box
       :width (:actions col-widths)
       :gap "2px"
       :align :center
       :children
       [[row-button
         :md-icon-name "zmdi zmdi-edit"
         :tooltip "Edit this OLD instance"
         :mouse-over-row? mouse-over-row?]
        [row-button
         :md-icon-name "zmdi zmdi-delete"
         :tooltip "Destroy this OLD instance"
         :mouse-over-row? mouse-over-row?]
        (when (and (:leader old-instance) (not (:auto-sync? old-instance)))
          [row-button
           :md-icon-name "zmdi zmdi-refresh-sync"
           :tooltip "Sync this local OLD with its leader"
           :mouse-over-row? mouse-over-row?])]]]]))

(defn old-instances-gui
  []
  (let [old-instances @(rf/subscribe [:old-instances])
        mouse-over (reagent/atom nil)]
    [v-box
     :class "rc-div-table"
     :children
     [[old-instances-gui-header]
       (for [old-instance (sort-by :slug old-instances)]
         ^{:key (:url old-instance)}
         [old-instances-gui-row old-instance mouse-over])]]))

(defn old-instances-section
  []
  [:div.old-instances-section
   {:style {}}
   [:h1 "Online Linguistic Database Instances"]
   [:p "These are your local Online Linguistic Database instances."]
   [:p (str "You may have to manually tell Dative about these OLD instances by"
            " adding new \"server\" instances for them under Dative >"
            " Application Settings.")]
   [old-instances-gui]])

(defn dativetop-box
  []
  [v-box
   :children
   [[box
     :align :center
     :child
     [title
      :label "DativeTop"
      :level :level1]]]])

;; To add CSS style: :style {:border "1px solid black"}

(defn old-service-box
  []
  [v-box
   :style {:padding "1em"}
   :children
   [[title :label "Online Linguistic Database" :level :level2]
    [:a
     {:href @(rf/subscribe [:old-service-url])}
     @(rf/subscribe [:old-service-url])]]])

(defn dative-app-box
  []
  [v-box
   :style {:padding "1em"}
   :children
   [[title :label "Dative" :level :level2]
    [:a
     {:href @(rf/subscribe [:dative-app-url])}
     @(rf/subscribe [:dative-app-url])]]])

(defn olds-box
  []
  [v-box
   :gap "10px"
   :children
   [[box
     :align :center
     :child
     [title
      :label "Online Linguistic Database Instances"
      :level :level2]]
    [v-box
     :align :center
     :children
     [[p "These are your local Online Linguistic Database instances."]
      [button
       :label "Fetch Server State"
       :on-click #(rf/dispatch [:poll-server-state])]
      [button
       :label "Reset Local State"
       :on-click #(rf/dispatch [:reset-local-state])]
      [p "You may have to manually tell Dative about these OLD instances by
         adding new \"server\" instances for them under Dative > Application
         Settings."]]]
    [old-instances-gui]]])

(defn margin-box
  []
  [box
   ;:style {:background-image "url(images/OLD-logo.png)"
   ;        :background-size "100%"
   ;        :background-repeat "no-repeat"}
   :child ""
   :size "2"])

(defn ui
  []
  [h-box
   :children
   [[margin-box]
    [v-box
     :style {:background-color "white"}
     :height "800px"
     :size "6"
     :align :center
     :children
     [[dativetop-box]
      [h-box
       :children
       [[old-service-box] [dative-app-box]]]]]
    [margin-box]]])

;; -- Entry Point -------------------------------------------------------------

(defn ^:export run
  []
  (rf/dispatch-sync [:init])
  (rf/dispatch-sync [:fetch-old-service])
  (rf/dispatch-sync [:fetch-dative-app])
  ;; mount the application's ui into '<div id="app" />'
  (reagent/render [ui] (js/document.getElementById "app")))
