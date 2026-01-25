import os
import gc
import warnings
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMessageBox
from utils.measurement import Body3D

from pprint import pprint
from SMPL_Anthropometry.measure import MeasureBody
from SMPL_Anthropometry.measurement_definitions import STANDARD_LABELS

@pyqtSlot()
def export_smpl(self):
    try:
        filename = self.NameExport.toPlainText().strip()
        if not filename:
            filename = "current_shape"
        filename += ".obj"

        full_path = os.path.join(self.args.output_path, filename)
        
        # outputフォルダが存在することを確認
        os.makedirs(self.args.output_path, exist_ok=True)
        
        self.smpl.save_to_obj(full_path)
        
        # 保存完了をユーザーに通知
        abs_path = os.path.abspath(full_path)
        QMessageBox.information(
            self,
            "Export Complete",
            f"OBJファイルを保存しました:\n{abs_path}"
        )
        print(f"Exported: {abs_path}")
        
    except Exception as e:
        QMessageBox.critical(
            self,
            "Export Error",
            f"ファイルの保存中にエラーが発生しました:\n{str(e)}"
        )
        print(f"Export error: {e}")


@pyqtSlot()
def print_params(self):
    print("====== Params ======")
    print(self.beta)
    
    # UIにダイアログで表示
    param_lines = ["Shape Parameters (Beta):", ""]
    for i, val in enumerate(self.beta):
        param_lines.append(f"β{i}: {val:.4f}")
    
    QMessageBox.information(
        self,
        "Shape Parameters",
        "\n".join(param_lines)
    )


@pyqtSlot()
def print_measures(self):
    try:
        # PyVistaのガベージコレクション問題を回避するため、警告を抑制
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            measurer = MeasureBody('smpl')
            measurer.from_body_model(gender='FEMALE', shape=self.beta)
            measurement_names = measurer.all_possible_measurements
            measurer.measure(measurement_names)
            measurer.label_measurements(STANDARD_LABELS)

            body_measurements = {
                'A (Height)': measurer.measurements['height'],
                'B (Chest)': measurer.measurements['chest circumference'],
                'C (Hip)': measurer.measurements['hip circumference'],
                'D (Waist)': measurer.measurements['waist circumference'],
                'E (Thigh L)': measurer.measurements['thigh left circumference'],
                'F (Outside Leg)': measurer.measurements['outside leg height'],
                'G (Inside Leg)': measurer.measurements['inside leg height'],
                'H (Shoulder-Crotch)': measurer.measurements['shoulder to crotch height'],
                'I (Shoulder Breadth)': measurer.measurements['shoulder breadth'],
            }

            # コンソールに出力
            print("====== Measures ======")
            print(body_measurements)
            
            # UIにダイアログで表示
            message_lines = ["Body Measurements (mm):", ""]
            for key, value in body_measurements.items():
                message_lines.append(f"{key}: {value:.1f}")
            
            QMessageBox.information(
                self,
                "Body Measurements",
                "\n".join(message_lines)
            )
            
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Error during measurement: {e}")
        print(error_detail)
        QMessageBox.critical(
            self,
            "Measurement Error",
            f"測定中にエラーが発生しました:\n{str(e)}"
        )
    finally:
        # 明示的にガベージコレクションを実行して不要なオブジェクトを解放
        try:
            gc.collect()
        except Exception:
            pass