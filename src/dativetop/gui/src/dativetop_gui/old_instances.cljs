(ns dativetop-gui.old-instances
  (:require [re-com.core   :refer [h-box v-box box gap line title label
                                   hyperlink-href input-text input-password
                                   button p single-dropdown md-icon-button
                                   modal-panel border info-button]]
            [re-frame.core :as re-frame]
            [dativetop-gui.utils  :refer [panel-title title2]]
            [dativetop-gui.login  :refer [old-instance-select]]
            [dativetop-gui.subs :as subs]
            [goog.string :as gstring]
            [goog.string.format]))

(defn active-old-section
  []
  [v-box
   :children [[h-box
               :children
               [[title :level :level2 :label "Current OLD"]
                [info-button
                 :info "This is the \"current\" OLD instance, i.e., the one
                       that your requests (e.g., to login or get all forms)
                       would be directed towards."]]]
              [gap :size "10px"]
              [old-instance-select]]])

(defn key-up-old-instance-input
  [e]
  (when (= "Enter" (.-key e))
    (re-frame/dispatch [:user-pressed-enter-in-old-input])))

(defn old-instance-url-input
  [old-instance-id old-instance-url]
  (let [url-statuses @(re-frame/subscribe [:old-instance-url-statuses])
        status-meta (get url-statuses old-instance-id)
        status (first status-meta)
        status-icon? (boolean status)
        status-tooltip (or (second status-meta) "")]
    [box
     :child
     [input-text
      :attr {:on-key-up key-up-old-instance-input}
      :change-on-blur? false
      :placeholder "OLD URL"
      :status status
      :status-icon? status-icon?
      :status-tooltip status-tooltip
      :model old-instance-url
      :on-change #(re-frame/dispatch
                    [:user-changed-old-instance-url old-instance-id %])]]))

(defn old-instance-name-input
  [old-instance-id old-instance-name]
  (let [name-statuses @(re-frame/subscribe [:old-instance-name-statuses])
        status-meta (get name-statuses old-instance-id)
        status (first status-meta)
        status-icon? (boolean status)
        status-tooltip (or (second status-meta) "")]
    [box
     :child
     [input-text
      :attr {:on-key-up key-up-old-instance-input}
      :change-on-blur? false
      :status status
      :status-icon? status-icon?
      :status-tooltip status-tooltip
      :placeholder "OLD name"
      :model old-instance-name
      :on-change #(re-frame/dispatch
                    [:user-changed-old-instance-label old-instance-id %])]]))

(defn delete-old-instance-button
  [old-instance-id]
  [md-icon-button
   :md-icon-name "zmdi-delete"
   :on-click #(re-frame/dispatch
                [:set-old-instance-to-be-deleted old-instance-id])])

(defn new-old-instance-button
  []
  [button
   :on-click
   (fn [e] (re-frame/dispatch [:user-clicked-create-new-old-instance-button]))
   :class "btn-success"
   :label "Create"])

(defn old-instance-view
  ([old-instance-id old-instance] (old-instance-view old-instance-id old-instance false))
  ([old-instance-id old-instance create?]
   [v-box
    :children
    [[gap :size "10px"]
     [h-box
      :align :center
      :children [[old-instance-name-input old-instance-id (:label old-instance)]
                 [gap :size "10px"]
                 [old-instance-url-input old-instance-id (:url old-instance)]
                 [gap :size "10px"]
                 (if create?
                   [new-old-instance-button]
                   [delete-old-instance-button old-instance-id])
                 ]]]]))

(defn new-old-instance-section
  []
  (let [new-old-instance @(re-frame/subscribe [:new-old-instance])]
    [v-box
     :children [[h-box
                 :children
                 [[title :level :level2 :label "New OLD Instance"]
                  [info-button
                   :info "Create a new OLD instance here. Note that this does
                         not literally create a new OLD instance on a server
                         somewhere. All it does is record the details of an OLD
                         instance in your browser so that you can interact with
                         that OLD instance."]]]
                [old-instance-view
                 (:id new-old-instance) new-old-instance true]]]))

(defn confirm-old-instance-delete-panel
  []
  (let [old-instance @(re-frame/subscribe [:old-instance-to-be-deleted])]
    (when old-instance
      (let [name (:label old-instance)
            uuid (:id old-instance)
            url (:url old-instance)]
        [modal-panel
         :backdrop-color "grey"
         :backdrop-opacity 0.4
         :style {:font-family "Consolas"}
         :backdrop-on-click
         #(re-frame/dispatch [:set-old-instance-to-be-deleted nil])
         :child
         [border
          :border "1px solid #eee"
          :child
          [v-box
           :padding  "10px"
           :style    {:background-color "cornsilk"}
           :children
           [[title :label "Confirm OLD Instance Deletion" :level :level2]
            [p (gstring/format
                 "Do you really want to delete the OLD instance named \"%s\"
                 (with URL \"%s\" and id \"%s\")?" name url (str uuid))]
            [line :color "#ddd" :style {:margin "10px 0 10px"}]
            [h-box
             :gap      "12px"
             :children [[button
                         :label    "Confirm"
                         :class    "btn-primary"
                         :on-click
                         #(re-frame/dispatch [:delete-old-instance uuid])]
                        [button
                         :label    "Cancel"
                         :on-click
                         #(re-frame/dispatch [:set-old-instance-to-be-deleted nil])
                         ]]]]]]]))))

(defn old-instances-section
  []
  (let [old-instances @(re-frame/subscribe [:old-instances])]
    [v-box
     :children [[h-box
                 :children
                 [[title :level :level2 :label "OLD Instances"]
                  [info-button
                   :info "These are the OLD instances that your Dative
                         application knows about. You can edit or delete them
                         if you like, but be careful: you don't want to lose
                         information about an OLD that you may want to interact
                         with."]]]
                (for [[id old-instance] old-instances]
                  ^{:key id}
                  [old-instance-view id old-instance])]]))

(defn old-instances-panel
  []
  [v-box
   :children
   [[panel-title "OLD Instances"]
    [active-old-section]
    [gap :size "30px"]
    [line]
    [new-old-instance-section]
    [gap :size "30px"]
    [line]
    [old-instances-section]
    [confirm-old-instance-delete-panel]
    ]])

(defn panel
  []
  [old-instances-panel])
