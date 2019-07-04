(ns dativetop-gui.subs
  (:require [re-frame.core :refer [reg-sub]]
            [dativetop-gui.utils  :refer [get-current-old-instance-url]]))

(reg-sub
 :name
 (fn [db]
   (:name db)))

(reg-sub
  :login-state
  (fn [db _] (get db :login-state)))


(reg-sub
  :current-tab
  (fn [db _] (get db :current-tab)))

(reg-sub
  :login-invalid-reason
  (fn [db _] (get db :login-invalid-reason)))

(reg-sub
  :new-old-invalid-reason
  (fn [db _] (get db :new-old-invalid-reason)))

(reg-sub
  :login-username-status
  :<- [:login-state]
  :<- [:login-invalid-reason]
  (fn [[login-state invalid-reason] _]
    (case login-state
      :login-requires-username [:error "Username required"]
      :login-is-invalid [:error invalid-reason]
      :user-is-authenticated [:success]
      :login-is-authenticating [:validating]
      [nil])))

(reg-sub
  :login-password-status
  :<- [:login-state]
  :<- [:login-invalid-reason]
  (fn [[login-state invalid-reason] _]
    (case login-state
      :login-requires-password [:error "Password required"]
      :login-is-invalid [:error invalid-reason]
      :user-is-authenticated [:success]
      :login-is-authenticating [:validating]
      [nil])))

(reg-sub
  :all-old-instances
  (fn [db _] (:old-instances db)))

(reg-sub
  :old-instance-states
  :<- [:all-old-instances]
  (fn [all-old-instances _]
    (reduce
      (fn [ret [id val]] (assoc ret id (:state val)))
      {}
      all-old-instances)))

(reg-sub
  :old-instance-url-statuses
  :<- [:old-instance-states]
  (fn [old-instance-states _]
    (reduce
      (fn [ret [id val]]
        (case val
          :requires-url (assoc ret id [:error "URL required"])
          (assoc ret id [nil])))
      {}
      old-instance-states)))

(reg-sub
  :old-instance-name-statuses
  :<- [:old-instance-states]
  (fn [old-instance-states _]
    (reduce
      (fn [ret [id val]]
        (case val
          :requires-label (assoc ret id [:error "Name required"])
          (assoc ret id [nil])))
      {}
      old-instance-states)))

(reg-sub
  :login-password
  (fn [db _] (get db :password)))

(reg-sub
  :login-username
  (fn [db _] (get db :username)))

(reg-sub
  :current-old-instance
  (fn [db _] (get db :current-old-instance)))

(reg-sub
  :old-instance-to-be-deleted
  (fn [db _]
    (let [old-uuid (:old-instance-to-be-deleted db)
          olds (:old-instances db)]
      (get olds old-uuid))))

(reg-sub
  :current-old-instance-url
  :<- [:current-old-instance]
  :<- [:old-instances]
  (fn [[current-old-instance old-instances] _]
    (:url (get old-instances current-old-instance))))

(reg-sub
  :new-old-instance
  (fn [db _] (get (:old-instances db) (:new-old-instance db))))

(reg-sub
  :old-instances
  (fn [db _]
    (into {}
          (filter
            (fn [[id _]] (not= id (:new-old-instance db)))
            (:old-instances db)))))

(reg-sub
  :old-instances-vec
  :<- [:old-instances]
  (fn [old-instances _] (into [] (vals old-instances))))

(reg-sub
  :login-disabled?
  :<- [:login-state]
  (fn [login-state _] (not= login-state :login-is-ready)))

(reg-sub
  :logout-disabled?
  :<- [:login-state]
  (fn [login-state _] (not= login-state :user-is-authenticated)))

(reg-sub
  :login-inputs-disabled?
  :<- [:login-state]
  (fn [login-state _] (= login-state :user-is-authenticated)))

(reg-sub
  :logged-in-old-name
  :<- [:login-state]
  :<- [:current-old-instance]
  :<- [:old-instances]
  (fn [[login-state current-old-instance old-instances] _]
    (when (= login-state :user-is-authenticated)
      (:label (get old-instances current-old-instance)))))

(reg-sub
  :forms
  (fn [db _] (:forms db)))

(reg-sub
  :visible-forms
  :<- [:forms]
  (fn [forms _]
    forms))

(reg-sub
  :selected-tab-id
  (fn [db _] (:selected-tab-id db)))

(reg-sub
  :focus-me
  (fn [db _] (:focus-me db)))
