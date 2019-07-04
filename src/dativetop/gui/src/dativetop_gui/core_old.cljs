(ns dativetop-gui.core-old
  (:require-macros [cljs.core.async.macros :refer [go]]
                   [secretary.core         :refer [defroute]])
  (:require [goog.events                   :as    events]
            [reagent.core                  :as    reagent]
            [re-frame.core                 :as    re-frame]
            [alandipert.storage-atom       :refer [local-storage]]
            [secretary.core                :as    secretary]
            [re-com.core                   :refer [h-box v-box box gap line scroller border label p title alert-box h-split] :refer-macros [handler-fn]]
            [re-com.util                   :refer [get-element-by-id item-for-id]]
            [goog.history.EventType        :as    EventType]
            ;; DativeTop GUI
            [dativetop-gui.config                 :as    config]
            [dativetop-gui.events                 :as    dativetop-gui-events]
            [dativetop-gui.forms                  :as    forms]
            [dativetop-gui.home                   :as    home]
            [dativetop-gui.login                  :as    login]
            [dativetop-gui.old-instances          :as    old-instances]
            [dativetop-gui.subs                   :as    dativetop-gui-subs]
            [dativetop-gui.utils                  :refer [dativetop-gui-title-box]])
  (:import [goog History]))

(def tabs-definition
  [{:id :home          :level :major :label "Home"   :panel home/panel}
   {:id :admin         :level :major :label "Admin"}
   {:id :login         :level :minor :label "Login"  :panel login/panel}
   {:id :old-instances :level :minor :label "OLDs"   :panel old-instances/panel}
   {:id :forms         :level :major :label "Forms"}
   {:id :forms-add     :level :minor :label "Add"    :panel forms/add-panel}
   {:id :forms-browse  :level :minor :label "Browse" :panel forms/browse-panel}
   ])


(defn scroll-to-top
  [element]
  (set! (.-scrollTop element) 0))


(defn nav-item
  []
  (let [mouse-over? (reagent/atom false)]
    (fn [tab selected-tab-id on-select-tab]
      (let [selected?   (= @selected-tab-id (:id tab))
            is-major?  (= (:level tab) :major)
            has-panel? (some? (:panel tab))]
        [:div
         {:style         {:white-space      "nowrap"
                          :line-height      "1.3em"
                          :padding-left     (if is-major? "24px" "32px")
                          :padding-top      (when is-major? "6px")
                          :font-size        (when is-major? "15px")
                          :font-weight      (when is-major? "bold")
                          :border-right     (when selected? "4px #d0d0d0 solid")
                          :cursor           (if has-panel? "pointer" "default")
                          :color            (if has-panel? (when selected? "#111") "#888")
                          :background-color (if (or
                                                  (= @selected-tab-id (:id tab))
                                                  @mouse-over?) "#eaeaea")}
          :on-mouse-over (handler-fn (when has-panel? (reset! mouse-over? true)))
          :on-mouse-out  (handler-fn (reset! mouse-over? false))
          :on-click      (handler-fn (when has-panel?
                                       (on-select-tab (:id tab))
                                       (scroll-to-top (get-element-by-id "right-panel"))))}
         [:span (:label tab)]]))))


(defn left-side-nav-bar
  [selected-tab-id on-select-tab]
    [v-box
     :class    "noselect"
     :style    {:background-color "#fcfcfc"}
     :children (for [tab tabs-definition]
                 [nav-item tab selected-tab-id on-select-tab])])



(defn browser-alert
  []
  [box
   :padding "10px 10px 0px 0px"
   :child   [alert-box
             :alert-type :danger
             :heading    "Only Tested On Chrome"
             :body       "Dative should work on all modern browsers, but there might be dragons!"]])


;; -- Routes, Local Storage and History ------------------------------------------------------

(defroute
  dativetop-gui-page
  "/:tab"
  [tab]
  (let [id (keyword tab)]
    (re-frame/dispatch [:set-selected-tab-id id])))


(def history (History.))

(events/listen
  history
  EventType/NAVIGATE
  (fn [event] (secretary/dispatch! (.-token event))))

(.setEnabled history true)


(defn logged-in-old-title-bar
  []
  (let [logged-in-old-name @(re-frame/subscribe [:logged-in-old-name])]
    (when logged-in-old-name
      [box
       :justify :center
       :align   :center
       :height  "62px"
       :style   {:background-color "#666"}
       :child [title
               :label logged-in-old-name
               :level :level1
               :style {:font-size "32px" :color "#fefefe"}]])))

(defn focuser
  []
  (let [focus-id @(re-frame/subscribe [:focus-me])]
    (println "focus this " focus-id)
    (let [inp (.getElementById js/document focus-id)]
      (if inp
        (do
          (println "focusing thing")
          (.focus inp))
        (println "not focusing thing")
        )
          ;char-idx (last focused-word)
                 ;_ (println "word " morph-list " should be focused")
                 ;]
             ;(.focus inp)
             ;(.setSelectionRange inp char-idx char-idx))))
    [:div])))

(defn main
  []
  ;; or can use (str "/" (name %1))
  (let [on-select-tab #(.setToken history (dativetop-gui-page {:tab (name %1)}))
        selected-tab-id (re-frame/subscribe [:selected-tab-id])]
    (fn
      []
      [h-split
       ;; Outer-most box height must be 100% to fill the entrie client height.
       ;; This assumes that height of <body> is itself also set to 100%.
       ;; width does not need to be set.
       :height   "100%"
       :initial-split 9
       :margin "0px"
       :panel-1 [scroller
                 :v-scroll :auto
                 :h-scroll :off
                 :child [v-box
                         :size "1"
                         :children [[dativetop-gui-title-box]
                                    ;[focuser]
                                    [left-side-nav-bar selected-tab-id on-select-tab]]]]
       :panel-2 [scroller
                 :attr  {:id "right-panel"}
                 :child [v-box
                         :size  "1"
                         :children [(when-not (-> js/goog .-labs .-userAgent
                                                  .-browser .isChrome)
                                      [browser-alert])
                                    [logged-in-old-title-bar]
                                    [box
                                     :padding "0px 0px 0px 50px"
                                     :child
                                     [(:panel
                                        (item-for-id @selected-tab-id
                                                     tabs-definition))]]]]]])))


(defn dev-setup []
  (when config/debug?
    (enable-console-print!)
    (println "dev mode")))


(defn mount-root []
  (re-frame/clear-subscription-cache!)
  (reagent/render [main] (get-element-by-id "app")))


(defn ^:export init []
  (re-frame/dispatch-sync [:app-was-initialized])
  (dev-setup)
  (mount-root))
