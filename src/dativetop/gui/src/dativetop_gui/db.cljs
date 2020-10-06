(ns dativetop-gui.db)


;; OLD Instances (web services) that this Dative knows about.
;; TODO: these should be received from the Dative server and/or stored in a
;; JSON/EDN file.
(def demo-old-1-uuid (random-uuid))
(def demo-old-2-uuid (random-uuid))
(def new-old-instance-uuid (random-uuid))
(def old-instances
  {demo-old-1-uuid {:id demo-old-1-uuid
                    :label "Pyramid OLD"
                    :url "http://127.0.0.1:61001/old/"
                    :state :ready}
   demo-old-2-uuid {:id demo-old-2-uuid
                    :label "Pylons OLD"
                    :url "http://127.0.0.1:5009/"
                    :state :ready}
   new-old-instance-uuid {:id new-old-instance-uuid
                          :label ""
                          :url ""
                          :state :ready}})

;; Forms that this

(def default-db
  {:selected-tab-id :home

   ;; Authentication state
   :username ""
   :password ""
   :login-state :login-is-ready
   :login-invalid-reason nil

   ;; OLD instances
   :old-instances old-instances
   :current-old-instance demo-old-1-uuid
   :new-old-instance new-old-instance-uuid
   :old-instance-to-be-deleted nil

   ;; Forms
   :forms-page 1
   :forms-items-per-page 10
   :forms-count 0
   ;; map from form IDs (int RDBMS pks) to forms (maps)
   :forms {}
   ;; map from form indices (calculated by dative-re-frame) to forms (maps)
   ;:forms-by-index {}

   :focus-me nil

   })
