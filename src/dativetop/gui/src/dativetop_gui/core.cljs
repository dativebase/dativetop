(ns dativetop-gui.core
  (:require [ajax.core :as ajax]
            [clojure.set :as set]
            [day8.re-frame.http-fx]
            [reagent.core :as reagent]
            [re-frame.core :as rf]
            [re-com.core :as rc :refer-macros [handler-fn]]))

;; -- Helpers & Data -----------------------------------------------------------

(def default-new-old
  {:slug ""
   :name ""
   :leader ""
   :username ""
   :password ""
   :is-auto-syncing? false})

(def default-db
  {:dativetop-server {:url js/DativeTopServerURL}
   :dative-app {:url js/DativeAppURL}
   :old-service {:url js/OLDServiceURL}
   :olds {}
   :old-edits {}
   :old-editor-visible? {}
   :old-delete-modal-visible? {}
   :new-old default-new-old
   :new-old-errors {}})

(def col-widths
  {:name "7.5em"
   :url "15em"
   :leader "20em"
   :state "8em"
   :is-auto-syncing? "8em"
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

;; -- Domino 1 - Event Dispatch -----------------------------------------------

;; -- Domino 2 - Event Handlers -----------------------------------------------

(rf/reg-fx
 :focus-to-element
 (fn [element-id]
   (reagent/after-render
    #(some-> js/document (.getElementById element-id) .focus))))

(rf/reg-event-fx
 :focus!
 (fn [{:keys [db]} [_ element-id]]
   {:db db
    :focus-to-element element-id}))

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

(rf/reg-event-fx
 :fetch-olds
 (fn [{{{dtserver-url :url} :dativetop-server :as db} :db} _]
   {:db db
    :http-xhrio
    {:method :get
     :headers {:Content-Type "application/json; utf8"}
     :format :json
     :uri (url :olds dtserver-url)
     :timeout 8000
     :response-format (ajax/json-response-format {:keywords? true})
     :on-success [:fetch-olds-success]
     :on-failure [:fetch-olds-failure]}}))

(rf/reg-event-db
 :fetch-olds-success
 (fn [db [_ olds]]
   (let [olds
         (->> olds
              (map (fn [{:keys [id] :as old}]
                     [id
                      (set/rename-keys
                       old {:is_auto_syncing :is-auto-syncing?})]))
              (into {}))]
     (-> db
         (assoc :olds olds)
         ;; only update OLD edits that have not been edited locally
         (update :old-edits
                 (fn [old-edits]
                   (reduce
                    (fn [old-edits [old-id old]]
                      (if-let [prev (get old-edits old-id)]
                        old-edits
                        (assoc old-edits old-id old)))
                    old-edits
                    olds)))))))

(rf/reg-event-db
 :fetch-olds-failure
 (fn [db [_ olds]]
   (print "fetch OLDs failure with ...")
   (print olds)
   db))

(defn validate-old [{:keys [slug]} olds]
  (cond
    (< (count slug) 3)
    {:slug "The slug must be at least three characters long"}
    (some #{slug} (map :slug olds))
    {:slug "That slug is already in use"}))

(rf/reg-event-fx
 :create-new-old
 (fn [{{{dtserver-url :url} :dativetop-server new-old :new-old :as db} :db} _]
   {:db db
    :http-xhrio
    {:method :post
     :headers {:Content-Type "application/json; utf8"}
     :format (ajax/json-request-format)
     :params (set/rename-keys new-old {:is-auto-syncing? :is_auto_syncing})
     :uri (url :olds dtserver-url)
     :timeout 8000
     :response-format (ajax/json-response-format {:keywords? true})
     :on-success [:create-new-old-success]
     :on-failure [:create-new-old-failure]}}))

(rf/reg-event-db
 :new-old-errors-event
 (fn [db [_ new-old-errors]]
   (assoc db :new-old-errors new-old-errors)))

(rf/reg-event-db
 :create-new-old-success
 (fn [db [_ {:keys [id] :as old}]]
   (-> db
       (assoc-in
        [:olds id]
        (set/rename-keys old {:is_auto_syncing :is-auto-syncing?}))
       (assoc :new-old default-new-old))))

(rf/reg-event-db
 :create-new-old-failure
 (fn [db [_ old]]
   (print "create new OLD failure with ...")
   (print old)
   db))

(rf/reg-event-fx
 :update-old
 (fn [{{{dtserver-url :url} :dativetop-server :keys [old-edits] :as db} :db}
      [_ id]]
   (let [updated-old (get old-edits id)]
     {:db db
      :http-xhrio
      {:method :put
       :headers {:Content-Type "application/json; utf8"}
       :format (ajax/json-request-format)
       :params (set/rename-keys updated-old {:is-auto-syncing? :is_auto_syncing})
       :uri (url :old dtserver-url id)
       :timeout 8000
       :response-format (ajax/json-response-format {:keywords? true})
       :on-success [:update-old-success]
       :on-failure [:update-old-failure]}})))

(rf/reg-event-db
 :update-old-success
 (fn [db [_ {:keys [id] :as old}]]
   (assoc-in
    db
    [:olds id]
    (set/rename-keys old {:is_auto_syncing :is-auto-syncing?}))))

(rf/reg-event-db
 :update-old-failure
 (fn [db [_ old]]
   (print "update OLD failure with ...")
   (print old)
   db))

(rf/reg-event-fx
 :delete-old
 (fn [{{{dtserver-url :url} :dativetop-server :as db} :db} [_ id]]
   {:db db
    :http-xhrio
    {:method :delete
     :headers {:Content-Type "application/json; utf8"}
     :format (ajax/json-request-format)
     :uri (url :old dtserver-url id)
     :timeout 8000
     :response-format (ajax/json-response-format {:keywords? true})
     :on-success [:delete-old-success]
     :on-failure [:delete-old-failure]}}))

(rf/reg-event-db
 :delete-old-success
 (fn [{:keys [olds old-edits old-editor-visible? old-delete-modal-visible?]
       :as db} [_ {:keys [id]}]]
   (-> db
       (assoc :olds (dissoc olds id))
       (assoc :old-edits (dissoc old-edits id))
       (assoc :old-editor-visible? (dissoc old-editor-visible? id))
       (assoc :old-delete-modal-visible? (dissoc old-delete-modal-visible? id)))))

(rf/reg-event-db
 :delete-old-failure
 (fn [db [_ old]]
   (print "delete OLD failure with ...")
   (print old)
   db))

(rf/reg-event-db
 :new-old-slug-event
 (fn [db [_ slug]]
   (-> db
       (assoc-in [:new-old :slug] slug)
       (update :new-old-errors #(dissoc % :slug)))))

(rf/reg-event-db
 :new-old-name-event
 (fn [db [_ name]] (assoc-in db [:new-old :name] name)))

(rf/reg-event-db
 :new-old-leader-event
 (fn [db [_ leader]] (assoc-in db [:new-old :leader] leader)))

(rf/reg-event-db
 :new-old-username-event
 (fn [db [_ username]] (assoc-in db [:new-old :username] username)))

(rf/reg-event-db
 :new-old-password-event
 (fn [db [_ password]] (assoc-in db [:new-old :password] password)))

(rf/reg-event-db
 :new-old-is-auto-syncing?-event
 (fn [db [_ is-auto-syncing?]]
   (assoc-in db [:new-old :is-auto-syncing?] is-auto-syncing?)))

(rf/reg-event-db
 :old-edits-slug-event
 (fn [db [_ id slug]] (assoc-in db [:old-edits id :slug] slug)))

(rf/reg-event-db
 :old-edits-name-event
 (fn [db [_ id name]] (assoc-in db [:old-edits id :name] name)))

(rf/reg-event-db
 :old-edits-leader-event
 (fn [db [_ id leader]] (assoc-in db [:old-edits id :leader] leader)))

(rf/reg-event-db
 :old-edits-username-event
 (fn [db [_ id username]] (assoc-in db [:old-edits id :username] username)))

(rf/reg-event-db
 :old-edits-password-event
 (fn [db [_ id password]] (assoc-in db [:old-edits id :password] password)))

(rf/reg-event-db
 :old-edits-is-auto-syncing?-event
 (fn [db [_ id is-auto-syncing?]]
   (assoc-in db [:old-edits id :is-auto-syncing?] is-auto-syncing?)))

(rf/reg-event-db
 :toggle-old-editor-visibility
 (fn [db [_ old-id]]
   (rf/dispatch [:focus! (str old-id "-name-input")])
   (update-in db [:old-editor-visible? old-id] not)))

(rf/reg-event-db
 :toggle-old-delete-modal-visibility
 (fn [db [_ old-id]]
   (let [visible (get-in db [:old-delete-modal-visible? old-id])]
     (if visible
       (assoc-in db [:old-delete-modal-visible? old-id] false)
       (do
         (rf/dispatch [:focus! (str old-id "-delete-cancel")])
         (assoc-in db [:old-delete-modal-visible? old-id] true))))))

;; -- Domino 4 - Query  -------------------------------------------------------

(rf/reg-sub
 :old-service-url
 (fn [db _]
   (-> db :old-service :url)))

(rf/reg-sub
 :dative-app-url
 (fn [db _]
   (-> db :dative-app :url)))

(rf/reg-sub :new-old-slug-error (fn [db _] (-> db :new-old-errors :slug)))

(rf/reg-sub :new-old (fn [db _] (:new-old db)))
(rf/reg-sub :new-old-slug (fn [db _] (-> db :new-old :slug)))
(rf/reg-sub :new-old-name (fn [db _] (-> db :new-old :name)))
(rf/reg-sub :new-old-leader (fn [db _] (-> db :new-old :leader)))
(rf/reg-sub :new-old-username (fn [db _] (-> db :new-old :username)))
(rf/reg-sub :new-old-password (fn [db _] (-> db :new-old :password)))
(rf/reg-sub :new-old-is-auto-syncing?
            (fn [db _] (-> db :new-old :is-auto-syncing?)))

(rf/reg-sub :olds (fn [db _] (-> db :olds vals)))

(rf/reg-sub
 :old
 (fn [db [_ old-id]]
   (get (:olds db) old-id {})))

(rf/reg-sub
 :old-edits
 (fn [db [_ old-id]]
   (get (:old-edits db)
        old-id
        (get (:olds db) old-id {}))))

(defn- get-old-edits [db old-id]
  (get (:old-edits db)
       old-id
       (get (:olds db) old-id {})))

(rf/reg-sub
 :old-edits-slug
 (fn [db [_ old-id]] (get (get-old-edits db old-id) :slug "")))

(rf/reg-sub
 :old-edits-name
 (fn [db [_ old-id]] (get (get-old-edits db old-id) :name "")))

(rf/reg-sub
 :old-edits-is-auto-syncing?
 (fn [db [_ old-id]] (get (get-old-edits db old-id) :is-auto-syncing? false)))

(rf/reg-sub
 :old-edits-leader
 (fn [db [_ old-id]] (get (get-old-edits db old-id) :leader "")))

(rf/reg-sub
 :old-edits-username
 (fn [db [_ old-id]] (get (get-old-edits db old-id) :username "")))

(rf/reg-sub
 :old-edits-password
 (fn [db [_ old-id]] (get (get-old-edits db old-id) :password "")))

(rf/reg-sub
 :old-editor-visible?
 (fn [db [_ old-id]]
   (get (:old-editor-visible? db)
        old-id
        false)))

(rf/reg-sub
 :old-delete-modal-visible?
 (fn [db [_ old-id]]
   (get (:old-delete-modal-visible? db)
        old-id
        false)))

;; -- Domino 5 - View Functions ----------------------------------------------

(defn olds-gui-header
  []
  [rc/h-box
   :class "rc-div-table-header"
   :children
   [[rc/label
     :label "Name"
     :width (:name col-widths)]
    [rc/label
     :label "URL"
     :width (:url col-widths)]
    [rc/label
     :label "Leader"
     :width (:leader col-widths)]
    [rc/label
     :label "State"
     :width (:state col-widths)]
    [rc/label
     :label "Auto-sync?"
     :width (:is-auto-syncing? col-widths)]
    [rc/label
     :label "Actions"
     :width (:actions col-widths)]]])

(defn delete-old-modal [{:keys [id slug]}]
  (let [hide #(rf/dispatch [:toggle-old-delete-modal-visibility id])
        keyboard-shortcuts (fn [event] (case (.-which event) 27 (hide) nil))]
    (when @(rf/subscribe [:old-delete-modal-visible? id])
      [rc/modal-panel
       :child
       [rc/v-box
        :children
        [[rc/p (str "Are you sure you want to delete the '"
                 slug
                 "' OLD?")]
         [rc/h-box
          :children
          [[rc/button
            :label "Delete"
            :class "btn-danger"
            :attr {:on-key-up keyboard-shortcuts}
            :style {:margin-right "15px"}
            :on-click #(rf/dispatch [:delete-old id])]
           [rc/button
            :label "Cancel"
            :attr {:id (str id "-delete-cancel")
                   :on-key-up keyboard-shortcuts}
            :on-click #(rf/dispatch [:toggle-old-delete-modal-visibility
                                     id])]]]]]])))

(defn edit-old-gui [id]
  (let [update-old (fn [] (rf/dispatch [:update-old id]))
        keyboard-shortcuts
        (fn [event] (case (.-which event)
                      13 (update-old)
                      27 (rf/dispatch [:toggle-old-editor-visibility id])
                      nil))
        visible? @(rf/subscribe [:old-editor-visible? id])]
    [rc/v-box
     :style {:display (if visible? "initial" "none")
             :padding "15px"}
     :children
     [[rc/title
       :label "Edit this OLD"
       :level :level4]
      [rc/h-box
       :style {:padding-top "15px"}
       :children
       [[rc/input-text
         :model @(rf/subscribe [:old-edits-slug id])
         :attr {:tab-index "1"
                :on-key-up keyboard-shortcuts}
         :disabled? true
         :placeholder "slug"
         :change-on-blur? false
         :on-change #(rf/dispatch [:old-edits-slug-event id %])]
        [rc/input-text
         :model @(rf/subscribe [:old-edits-name id])
         :attr {:tab-index "1"
                :id (str id "-name-input")
                :on-key-up keyboard-shortcuts}
         :style {:margin-left "15px"}
         :placeholder "name"
         :change-on-blur? false
         :on-change #(rf/dispatch [:old-edits-name-event id %])]
        [rc/checkbox
         :model @(rf/subscribe [:old-edits-is-auto-syncing? id])
         :attr {:tab-index "1"
                :on-key-up keyboard-shortcuts}
         :style {:margin-left "30px"}
         :label "auto-sync?"
         :on-change #(rf/dispatch [:old-edits-is-auto-syncing?-event id %])]]]
      [rc/h-box
       :style {:padding-top "15px"}
       :children
       [[rc/input-text
         :model @(rf/subscribe [:old-edits-leader id])
         :attr {:tab-index "1"
                :on-key-up keyboard-shortcuts}
         :placeholder "remote OLD URL"
         :change-on-blur? false
         :on-change #(rf/dispatch [:old-edits-leader-event id %])]
        [rc/input-text
         :model @(rf/subscribe [:old-edits-username id])
         :attr {:tab-index "1"
                :on-key-up keyboard-shortcuts}
         :style {:margin-left "15px"}
         :placeholder "remote OLD username"
         :change-on-blur? false
         :on-change #(rf/dispatch [:old-edits-username-event id %])]
        [rc/input-password
         :model @(rf/subscribe [:old-edits-password id])
         :attr {:tab-index "1"
                :on-key-up keyboard-shortcuts}
         :style {:margin-left "30px"}
         :placeholder "remote OLD password"
         :change-on-blur? false
         :on-change #(rf/dispatch [:old-edits-password-event id %])]]]
      [rc/box
       :style {:padding-top "15px"}
       :child
       [rc/button
        :label "Update"
        :attr {:tab-index "1"}
        :on-click #(rf/dispatch [:update-old id])]]]]))

(defn old-gui-row
  [{old-name :name :keys [id slug leader state is-auto-syncing?]
    :or {leader ""} :as old}
   old-service-url mouse-over]
  (let [mouse-over-row? (identical? @mouse-over old)
        old-url (str old-service-url "/" slug)]
    [rc/v-box
     :children
     [[rc/h-box
       :class "rc-div-table-row"
       :attr {:on-mouse-over (handler-fn (reset! mouse-over old))
              :on-mouse-out  (handler-fn (reset! mouse-over nil))}
       :children
       [[rc/scroller
         :h-scroll :auto
         :width (:name col-widths)
         :child [rc/label :label old-name]]
        [rc/scroller
         :h-scroll :auto
         :width (:url col-widths)
         :child [rc/label :label [:a {:href old-url} old-url]]]
        [rc/scroller
         :h-scroll :auto
         :width (:leader col-widths)
         :child [rc/label :label [:a {:href leader} leader]]]
        [rc/label
         :label state
         :width (:state col-widths)]
        [rc/label
         :label (str is-auto-syncing?)
         :width (:is-auto-syncing? col-widths)]
        [rc/h-box
         :width (:actions col-widths)
         :gap "2px"
         :align :center
         :children
         [[rc/row-button
           :md-icon-name "zmdi zmdi-edit"
           :tooltip "Edit this OLD instance"
           :mouse-over-row? mouse-over-row?
           :on-click #(rf/dispatch [:toggle-old-editor-visibility id])]
          [rc/row-button
           :md-icon-name "zmdi zmdi-delete"
           :tooltip "Destroy this OLD instance"
           :mouse-over-row? mouse-over-row?
           :on-click #(rf/dispatch [:toggle-old-delete-modal-visibility id])]]]]]
      [edit-old-gui id]
      [delete-old-modal old]]]))

(defn olds-gui []
  (let [olds @(rf/subscribe [:olds])
        old-service-url @(rf/subscribe [:old-service-url])
        mouse-over (reagent/atom nil)]
    [rc/v-box
     :class "rc-div-table"
     :children
     [[olds-gui-header]
      (for [old (sort-by :slug olds)]
        ^{:key (:id old)}
        [old-gui-row old old-service-url mouse-over])]]))

(defn dativetop-box
  []
  [rc/v-box
   :children
   [[rc/box
     :align :center
     :child
     [rc/title
      :label "DativeTop"
      :level :level1]]]])

(defn old-service-box
  []
  [rc/v-box
   :style {:padding "1em"}
   :children
   [[rc/title :label "Online Linguistic Database server" :level :level2]
    [:a
     {:href @(rf/subscribe [:old-service-url])}
     @(rf/subscribe [:old-service-url])]]])

(defn dative-app-box []
  [rc/v-box
   :style {:padding "1em"}
   :children
   [[rc/title :label "Dative app" :level :level2]
    [:a
     {:href @(rf/subscribe [:dative-app-url])}
     @(rf/subscribe [:dative-app-url])]]])

(defn create-new-old [& _]
  (let [new-old @(rf/subscribe [:new-old])
        olds @(rf/subscribe [:olds])
        errors (validate-old new-old olds)]
    (if errors
      (rf/dispatch [:new-old-errors-event errors])
      (rf/dispatch [:create-new-old]))))

(defn create-new-old-on-return-key [event]
  (when (= 13 (.-which event)) (create-new-old)))

(defn create-old-box []
  [rc/v-box
   :children
   [[rc/title
     :label "Create a new OLD"
     :level :level2]
    [rc/h-box
     :style {:padding-top "15px"}
     :children
     [[rc/input-text
       :model @(rf/subscribe [:new-old-slug])
       :attr {:tab-index "1"
              :auto-focus true
              :on-key-up create-new-old-on-return-key}
       :status (and @(rf/subscribe [:new-old-slug-error]) :error)
       :status-icon? true
       :status-tooltip @(rf/subscribe [:new-old-slug-error])
       :placeholder "slug"
       :change-on-blur? false
       :validation-regex #"^[a-zA-Z0-9_-]{0,20}$"
       :on-change #(rf/dispatch [:new-old-slug-event %])]
      [rc/input-text
       :model @(rf/subscribe [:new-old-name])
       :attr {:tab-index "1"
              :on-key-up create-new-old-on-return-key}
       :style {:margin-left "15px"}
       :placeholder "name"
       :change-on-blur? false
       :on-change #(rf/dispatch [:new-old-name-event %])]
      [rc/checkbox
       :model @(rf/subscribe [:new-old-is-auto-syncing?])
       :attr {:tab-index "1"
              :on-key-up create-new-old-on-return-key}
       :style {:margin-left "30px"}
       :label "auto-sync?"
       :on-change #(rf/dispatch [:new-old-is-auto-syncing?-event %])]]]
    [rc/h-box
     :style {:padding-top "15px"}
     :children
     [[rc/input-text
       :model @(rf/subscribe [:new-old-leader])
       :attr {:tab-index "1"
              :on-key-up create-new-old-on-return-key}
       :placeholder "remote OLD URL"
       :change-on-blur? false
       :on-change #(rf/dispatch [:new-old-leader-event %])]
      [rc/input-text
       :model @(rf/subscribe [:new-old-username])
       :attr {:tab-index "1"
              :on-key-up create-new-old-on-return-key}
       :style {:margin-left "15px"}
       :placeholder "remote OLD username"
       :change-on-blur? false
       :on-change #(rf/dispatch [:new-old-username-event %])]
      [rc/input-password
       :model @(rf/subscribe [:new-old-password])
       :attr {:tab-index "1"
              :on-key-up create-new-old-on-return-key}
       :style {:margin-left "30px"}
       :placeholder "remote OLD password"
       :change-on-blur? false
       :on-change #(rf/dispatch [:new-old-password-event %])]]]
    [rc/box
     :style {:padding-top "15px"}
     :child
     [rc/button
      :label "Create"
      :attr {:tab-index "1"}
      :on-click create-new-old]]]])

(defn list-olds-box []
  [rc/v-box
   :style {:margin-bottom "3em"}
   :children
   [[rc/title
     :label "Online Linguistic Database instances"
     :level :level2]
    [rc/box :style {:padding-top "15px"} :child ""]
    [olds-gui]]])

(defn olds-box []
  [rc/v-box
   :gap "10px"
   :children
   [[create-old-box]
    [list-olds-box]]])

(defn ui
  []
  [rc/h-box
   :children
   [[rc/v-box
     :style {:background-color "white"}
     :height "800px"
     :size "6"
     :align :center
     :children
     [[dativetop-box]
      [rc/h-box
       :children
       [[old-service-box] [dative-app-box]]]
      [olds-box]]]]])

;; -- Entry Point -------------------------------------------------------------

(defn fetch-olds-dispatch []
  (rf/dispatch [:fetch-olds]))

;; Fetch the OLDs every 2 seconds.
;; `defonce` is like `def` but it ensures only instance is ever
;; created in the face of figwheel hot-reloading of this file.
(defonce fetch-olds-timer (js/setInterval fetch-olds-dispatch 2000))

(defn ^:export run
  []
  (rf/dispatch-sync [:init])
  (rf/dispatch-sync [:fetch-old-service])
  (rf/dispatch-sync [:fetch-dative-app])
  (rf/dispatch-sync [:fetch-olds])
  ;; mount the application's ui into '<div id="app" />'
  (reagent/render [ui] (js/document.getElementById "app")))
