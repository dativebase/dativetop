(ns dativetop-gui.home
  (:require [re-com.core   :refer [h-box v-box box gap line title label
                                   hyperlink-href input-text p]]
            [dativetop-gui.utils  :refer [panel-title title2 RHS-column-style
                                   center-gap-px]]))


(defn welcome
  []
  [v-box
   :children [[gap :size "10px"]
              [p
               "Dative-Re-frame is a GUI for interacting with "
               [hyperlink-href
                :label "Online Linguistic Database (OLD)"
                :href "http://www.onlinelinguisticdatabase.org/"
                :target "_blank"]
               " instances ."]
              [h-box
               :gap center-gap-px
               :children
               [
                [p "Dative/OLD (known collectively as "
                 [:span.bold "DativeBase"]
                 ") is software for linguistic analysis and language
                 documentation. It is a linguistic data management system."]
                [p RHS-column-style
                 [:br]
                 "The github repo "
                 [hyperlink-href
                  :label "is here"
                  :href "https://github.com/dativebase/dative-re-frame"
                  :target "_blank"] "."]]]]])


(defn features
  []
  [v-box
   :children [
              [title :level :level2 :label "Features"]
              [gap :size "10px"]
              [:ul
               [:li "Collaboration and data sharing"] 
               [:li "Advanced and smart search"]
               [:li "Automatic morpheme cross-referencing"]
               [:li "Build morphological parsers and phonologies"]
               [:li "CSV import"]
               [:li "Text creation"]
               [:li "Media file (i.e., audio, video, image)-to-text association."]
               [:li "User access control"]
               [:li "Documentation"]
               [:li "Open source"]]]])


(defn panel2
  []
  [v-box
   :children [[panel-title "Dative"]
              [gap :size "15px"]
              [welcome]
              [gap :size "30px"]
              [line]
              [features]
              [gap :size "30px"]
              ]])


;; core holds a reference to panel, so need one level of indirection to get
;; figwheel updates
(defn panel
  []
  [panel2])
