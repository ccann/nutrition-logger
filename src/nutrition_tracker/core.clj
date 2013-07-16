(ns nutrition-tracker.core
  (:use (clojure.java.io)
        [clojure.string :only (split)]
        (seesaw.core))
  (:import (java.util Date)
           (java.text SimpleDateFormat)
           (java.io FileNotFoundException)))

(defrecord Food [name portion kcal prot carb fat])
(def fridge-loc "database/fridge.csv")
(def db "database/")
(def db-ext ".log")

(def lift-day {:kcals 1800, :protein 157, :carbs 219, :fat 33})
(def rest-day {:kcals 1400, :protein 157, :carbs 58, :fat 64})

(def fridge
  (with-open [rdr (reader fridge-loc)]
    (let [lines (doall (line-seq rdr))]
      (for [line lines]
        (let [l (split line #",")
              name (nth l 0)
              port (nth l 1)
              kcal (nth l 2)
              prot (nth l 3)
              carb (nth l 4)
              fats (nth l 5)]
          (Food. name port kcal prot carb fats))))))

;; write to a new log file the date and the type (e.g. "lift" "rest")
;; (defn create-log [date & type]
;;   (with-open [wrt (writer (str db date db-ext))]
;;     (.write wrt (str date "," type \newline))))

;; write this food to fridge.csv
(defn stock-fridge [food]
  (with-open [wrt (writer fridge-loc :append true)]
    (.write wrt (str (apply str (interpose "," (vals food))) \newline))))

;; write this food to log at database/date.log
(defn log [food]
  (let [date (java.util.Date.)
        sdf (java.text.SimpleDateFormat. "MM.dd.yyyy")
        dt (.format sdf date)]
    (with-open [wrt (writer (str db dt db-ext) :append true)]
           (do (stock-fridge food)
               (.write wrt (str (apply str (interpose "," (vals food))) \newline))))))

;; read *stdin* 
(defn read-args [& args]
  (loop [input (read-line)]
    (when-not (= ":done" input)
      (println (str "You entered: >>" input "<<"))
      (recur (read-line)))))

(defn -main [& args]
  (read-args args))


(def button-create-log (button :text "Create new log"))


;; (defn -main [args]
;;   (-> (frame :title "Nutrition Tracker",
;;              :content "Hi",
;;              :size [640 :by 480]
;;              :on-close :hide)
;;       pack!
;;       show!))
