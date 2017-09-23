# JJJProgramSpec
自立循環型住宅プロジェクトで開発しているプログラムの仕様書やテスト用スクリプトです。

## 基本情報
1. [インターフェース仕様書](InterfaceSpec/spec_general.adoc)

## 自然風の利用・制御
1. [インターフェース仕様書](InterfaceSpec/spec_natural_ventilation.adoc)
1. 関連する計算方法仕様書  
[第3章 暖冷房負荷と外皮性能 第1章 全般](CalculationSpec/03_HCLoad_01_General.adoc)

## 昼光利用
1. [インターフェース仕様書](InterfaceSpec/spec_daiylight.adoc)

## 太陽光発電
1. [インターフェース仕様書](InterfaceSpec/spec_PV.adoc)
1. 関連する計算方法仕様書  
[第9章 太陽光発電設備](CalculationSpec/09PV.adoc)

## 蓄熱の利用
1. [インターフェース仕様書](InterfaceSpec/spec_thermal_storage.adoc)
1. 関連する計算方法仕様書
[第3章 暖冷房負荷と外皮性能 第1章 全般](CalculationSpec/03_HCLoad_01_General.adoc)
[第3章 暖冷房負荷と外皮性能 第1章 全般 付録B](CalculationSpec/03_HCLoad_01_General_App_B.adoc)

## 屋根空気集熱式ソーラーシステム
1. 準備中

## 太陽熱給湯
1. [インターフェース仕様書](InterfaceSpec/spec_solar_heat_supply.adoc)

## 断熱外皮計画
1. [インターフェース仕様書](InterfaceSpec/spec_thermal_insulation.adoc)
1. 関連する計算方法仕様書
[第3章 暖冷房負荷と外皮性能 第2章 外皮性能](03_HCLoad_02_EnvelopePerformance.adoc)
[第3章 暖冷房負荷と外皮性能 第2章 外皮性能 付録B](03_HCLoad_02_EnvelopePerformance_App_B.adoc)
[第3章 暖冷房負荷と外皮性能 第2章 外皮性能 付録C](03_HCLoad_02_EnvelopePerformance_App_C.adoc)


## 日射熱制御(日射遮蔽・日射熱の利用)
1. [インターフェース仕様書](InterfaceSpec/spec_solar_shade_and_gain.adoc)
1. 関連する計算方法仕様書
[第3章 暖冷房負荷と外皮性能 第2章 外皮性能](03_HCLoad_02_EnvelopePerformance.adoc)
[第3章 暖冷房負荷と外皮性能 第2章 外皮性能 付録B](03_HCLoad_02_EnvelopePerformance_App_B.adoc)
[第3章 暖冷房負荷と外皮性能 第2章 外皮性能 付録C](03_HCLoad_02_EnvelopePerformance_App_C.adoc)
1. 根拠資料
[隣棟を考慮した方位係数の低減係数の計算根拠と計算方法](bases/DistanceCoefficientDegradation.ipynb)
[隣棟を考慮した方位係数の精緻解の結果(EP&B伊藤氏 報告書による)](bases/DistanceCoefficientDegradationData.csv)

## 断熱外皮計画　日射熱制御　共通
1. [面積を入力しない方法におけるUA値とηA値の計算方法](JJJDetuchedHouseEnvelopeSimpleEvaluationMethod.ipynb)
1. [面積を入力しない方法におけるUA値とηA値の計算方法のテスト](JJJDetuchedHouseEnvelopeSimpleEvaluationMethodTest.ipynb)
1. [部位ごとのU値の計算方法と計算方法のテスト(別のテストファイルに分離していない)](JJJUValueSimpleEvaluationMethod.ipynb)


## 暖房設備計画
1. [インターフェース仕様書](InterfaceSpec/spec_heating_system.adoc)

## 冷房設備計画
1. [インターフェース仕様書](InterfaceSpec/spec_cooling_system.adoc)

## 換気設備計画
1. [インターフェース仕様書](InterfaceSpec/spec_mechanical_ventilation.adoc)

## 給湯設備計画
1. [インターフェース仕様書](InterfaceSpec/spec_DHW.adoc)

## 照明設備計画
1. [インターフェース仕様書](InterfaceSpec/spec_lighting.adoc)

## 高効率家電機器の導入
1. [インターフェース仕様書](InterfaceSpec/spec_appliances.adoc)

## コージェネレーションシステムの導入
1. [インターフェース仕様書](InterfaceSpec/spec_cogeneration.adoc)

## 水と生ゴミの処理と効率的利用
1. [インターフェース仕様書](InterfaceSpec/spec_water_and_kitchen_waste.adoc)
