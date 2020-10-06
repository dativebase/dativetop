;; View functions for Dative's login panel

;; Functions that return re-com widget components which react (i.e., modify the
;; DOM, or subscribe) to events emitted by the app database and which trigger
;; events based on a user's interaction with the GUI.

;; All Dative view modules should define a ``panel`` function.

(ns dativetop-gui.login
  (:require [re-com.core   :refer [h-box v-box box gap line title label
                                   hyperlink-href input-text input-password
                                   button p single-dropdown]]
            [re-frame.core :as re-frame]
            [dativetop-gui.utils  :refer [panel-title title2 RHS-column-style
                                   center-gap-px]]
            [dativetop-gui.subs   :as subs]))


(defn key-up-login-input
  [e]
  (when (= "Enter" (.-key e))
    (re-frame/dispatch [:user-pressed-enter-in-login])))


(defn old-instance-select
  []
  [h-box
   :gap "10px"
   :align :center
   :children [[box
               :child [single-dropdown
                       :width "250px"
                       :choices @(re-frame/subscribe [:old-instances-vec])
                       :model @(re-frame/subscribe [:current-old-instance])
                       :on-change #(re-frame/dispatch
                                     [:user-changed-current-old-instance %])
                       :disabled? @(re-frame/subscribe [:login-inputs-disabled?])]]
              [v-box
               :children
               [[gap :size "10px"]
                [p
                 RHS-column-style
                 @(re-frame/subscribe [:current-old-instance-url])]]]]])


(defn username-input
  []
  (let [status-meta @(re-frame/subscribe [:login-username-status])
        status (first status-meta)
        status-icon? (boolean status)
        status-tooltip (or (second status-meta) "")]
    [box
     :child
     [input-text
      :attr {:on-key-up key-up-login-input}
      :status status
      :status-icon? status-icon?
      :status-tooltip status-tooltip
      :change-on-blur? false
      :placeholder "username"
      :model @(re-frame/subscribe [:login-username])
      :disabled? @(re-frame/subscribe [:login-inputs-disabled?])
      :on-change #(re-frame/dispatch [:user-changed-username %])]]))


(defn password-input
  []
  (let [status-meta @(re-frame/subscribe [:login-password-status])
        status (first status-meta)
        status-icon? (boolean status)
        status-tooltip (or (second status-meta) "")]
    [box
     :child
     [input-password
      :attr {:on-key-up key-up-login-input}
      :status status
      :status-icon? status-icon?
      :status-tooltip status-tooltip
      :placeholder "password"
      :change-on-blur? false
      :model @(re-frame/subscribe [:login-password])
      :disabled? @(re-frame/subscribe [:login-inputs-disabled?])
      :on-change #(re-frame/dispatch [:user-changed-password %])]]))


(defn login-button
  []
  [box
   :child
   [button
    :label "Login"
    :disabled? @(re-frame/subscribe [:login-disabled?])
    :on-click (fn [e] (re-frame/dispatch [:user-clicked-login]))]])


(defn logout-button
  []
  [box
   :child
   [button
    :label "Logout"
    :disabled? @(re-frame/subscribe [:logout-disabled?])
    :on-click (fn [e] (re-frame/dispatch [:user-clicked-logout]))]])


(defn login-panel
  []
  [v-box
   :children [[panel-title "Login"]
              [gap :size "10px"]
              [old-instance-select]
              [gap :size "10px"]
              [username-input]
              [gap :size "10px"]
              [password-input]
              [gap :size "10px"]
              [h-box
               :children [[login-button]
                          [logout-button]]
               :gap "5px"]]])


(defn panel
  []
  [login-panel])
