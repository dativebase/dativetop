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
            [goog.string.format]))

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

(defn fetch-data
  []
  nil)

;; -- Domino 1 - Event Dispatch -----------------------------------------------

(defn dispatch-poll-server-state-event [] (rf/dispatch [:poll-server-state]))

(defonce poller (js/setInterval dispatch-poll-server-state-event 1000))

;; -- Domino 2 - Event Handlers -----------------------------------------------

(def get-server-state-map
  {:method :get
   :headers {:Content-Type "application/json; utf8"}
   :format :json
   :uri "http://127.0.0.1:6543/"
   :timeout 8000
   :response-format (ajax/json-response-format {:keywords? true})})

(rf/reg-event-fx
 :initialize
 (fn [{:keys [db]} _]
   {:db db
    :http-xhrio (-> get-server-state-map
                    (assoc :on-success [:initialize-success])
                    (assoc :on-failure [:initialize-failure]))}))

(rf/reg-event-fx
 :poll-server-state
 (fn [{:keys [db]} _]
   (if (:dirty? db)
     {:db db}
     {:db db
      :http-xhrio (-> get-server-state-map
                      (assoc :on-success [:poll-server-state-success])
                      (assoc :on-failure [:poll-server-state-failure]))})))

(def default-db
  {:dative-url ""
   :old-url ""
   :new-old {:name ""
             :short-name ""
             :leader ""}
   :old-instances {}
   :server-state {}
   :dirty? false})

(rf/reg-event-db
 :initialize-success
 (fn [db [_ r]]
   (merge default-db r)))

(rf/reg-event-db
 :initialize-failure
 (fn [db _]
   default-db))

(rf/reg-event-db
 :poll-server-state-success
 (fn [db [_ r]]
   (if (:dirty? db)
     (assoc db :server-state r)
     (merge db r))))

(rf/reg-event-db
 :poll-server-state-failure
 (fn [db _]
   db))

(rf/reg-event-db
  :new-old-create
  (fn [db _]
    (let [new-old (:new-old db)]
      (js/console.log "You want to create a new OLD called with this data:")
      (js/console.log new-old)
      (if (new-old-valid? new-old)
        (js/console.log "valid!")
        (js/console.log "invalid :("))
      db)))

(rf/reg-event-db
  :new-old-name-change
  (fn [db [_ new-name]]
    (assoc-in db [:new-old :name] new-name)))

(rf/reg-event-db 
  :auto-sync?-changed-DEPRECATED
  (fn [db [_ old-url auto-sync?-val]]
    (assoc-in db [:old-instances (keyword old-url) :auto-sync?] auto-sync?-val)))

(rf/reg-event-fx
 :auto-sync?-changed
 (fn [{:keys [db]} [_ old-url auto-sync?-val]]
   (let [old-url-kw (keyword old-url)
         current-oi (get-in db [:old-instances old-url-kw])
         updated-oi (assoc current-oi :auto-sync? auto-sync?-val)]
     {:db (assoc db :dirty? true)
      :http-xhrio {:method :put
                   :params updated-oi
                   :timeout 5000
                   :format (ajax/json-request-format)
                   :headers {:Content-Type "application/json; utf8"}
                   :uri "http://127.0.0.1:6543/"
                   :response-format (ajax/json-response-format {:keywords? true})
                   :on-success [:auto-sync?-change-success]
                   :on-failure [:auto-sync?-change-failure]}})))

(rf/reg-event-db
 :auto-sync?-change-success
 (fn [db [_ r]]
   (println "auto-sync? changed on server")
   (-> db
       (assoc :dirty? false)
       (merge r))))

(rf/reg-event-db
 :auto-sync?-change-failure
 (fn [db _]
   (println "auto-sync? FAILED to change on server")
   (assoc db :dirty? false)))

(rf/reg-event-db
  :new-old-short-name-change
  (fn [db [_ new-short-name]]
    (assoc-in db [:new-old :short-name] new-short-name)))

(rf/reg-event-db
  :new-old-leader-change
  (fn [db [_ new-leader]]
    (assoc-in db [:new-old :leader] new-leader)))

;; -- Domino 4 - Query  -------------------------------------------------------

(rf/reg-sub
  :old-instances
  (fn [db _]
    (:old-instances db)))

(rf/reg-sub
  :new-old-name
  (fn [db _]
    (get-in db [:new-old :name])))

(rf/reg-sub
  :new-old-short-name
  (fn [db _]
    (get-in db [:new-old :short-name])))

(rf/reg-sub
  :new-old-leader
  (fn [db _]
    (get-in db [:new-old :leader])))

(rf/reg-sub
  :dative-url
  (fn [db _]
    (:dative-url db)))

;; -- Domino 5 - View Functions ----------------------------------------------

(defn data-row
  [row first? last?]
  [h-box
   :class    "rc-div-table-row"
   :children
   [
    [label
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
       (for [old-instance (sort-by :name (vals old-instances))]
         ^{:key (:url old-instance)}
         [old-instances-gui-row old-instance mouse-over])]]))

(defn old-instances-div-DEPRECATED
  []
  (let [old-instances @(rf/subscribe [:old-instances])]
    [data-table old-instances]
    [:table.old-instances
     [:thead
      [:tr
       [:th "Name"]
       [:th "URL"]
       [:th "Leader"]
       [:th "Actions"]]]
     [:tbody
      (map format-old-instance-row (vals old-instances))
      [:tr
        [:td
        [:input.new-old-name-input
          {:type "text"
           :id "new-old-name"
           :value @(rf/subscribe [:new-old-name])
           :on-change #(rf/dispatch [:new-old-name-change (-> % .-target .-value)])}]]
        [:td
        [:input.new-old-short-name-input
          {:type "text"
           :id "new-old-short-name"
           :value @(rf/subscribe [:new-old-short-name])
           :on-change #(rf/dispatch [:new-old-short-name-change (-> % .-target .-value)])}]]
        [:td
        [:input.new-old-leader-input
          {:type "text"
           :id "new-old-leader"
           :value @(rf/subscribe [:new-old-leader])
           :on-change #(rf/dispatch [:new-old-leader-change (-> % .-target .-value)])}]]
        [:td
        [:button
          {:on-click #(rf/dispatch [:new-old-create])}
          "Create"]]]]]))

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
      :level :level1]]
    [p "The DativeTop is an application for linguistic data management."]
    [p "It lets you manage Online Linguistic Database (OLD) instances on your
       local machine and configure them to sync with leader OLDs on the web."]
    [p "DativeTop lets you use the Dative graphical user interface to work with
       your OLD instances."]]])

(defn dative-box
  []
  [v-box
   :children
   [[box
     :align :center
     :child
     [title
      :label "Dative"
      :level :level2]]
    [v-box
     :children
     [[p
       "Your local Dative app is being served at "
       [:a {:href @(rf/subscribe [:dative-url])} @(rf/subscribe [:dative-url])]
       "."]
      [p "To view Dative, click the \"View\" menu item and then \"Dative\".
         Click the \"Help\" menu item and then \"Visit Dative in Browser\" to
         open Dative in your web browser."]]]]])

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
      [dative-box]
      [olds-box]]]
    [margin-box]
    ]])

;; -- Entry Point -------------------------------------------------------------

(defn ^:export run
  []
  (rf/dispatch-sync [:initialize])     ;; puts a value into application state
  (reagent/render [ui]              ;; mount the application's ui into '<div id="app" />'
                  (js/document.getElementById "app")))
