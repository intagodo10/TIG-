"""
Vista de gestión de pacientes.

Permite crear, editar y visualizar información de pacientes.
"""

import customtkinter as ctk
from typing import Optional, Callable
from datetime import datetime

from config.ui_theme import COLORS, FONTS
from models.patient import Patient, Sex, AffectedLimb
from utils.validators import validate_patient_id, validate_patient_data
from utils.logger import get_logger

logger = get_logger(__name__)


class PatientView(ctk.CTkFrame):
    """
    Vista principal de gestión de pacientes.

    Permite ingresar y editar información del paciente.
    """

    def __init__(self, master, on_patient_saved: Optional[Callable] = None, **kwargs):
        """
        Inicializa la vista de paciente.

        Args:
            master: Widget padre
            on_patient_saved: Callback cuando se guarda un paciente
        """
        super().__init__(master, **kwargs)

        self.on_patient_saved = on_patient_saved
        self.current_patient: Optional[Patient] = None

        self.configure(fg_color=COLORS["bg_primary"])

        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets de la vista."""
        # Scroll frame principal
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_primary"]
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = ctk.CTkLabel(
            scroll_frame,
            text="Información del Paciente",
            font=ctk.CTkFont(size=FONTS["size_xxlarge"], weight=FONTS["weight_bold"]),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(pady=(0, 20), anchor="w")

        # Frame del formulario
        form_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["bg_secondary"], corner_radius=12)
        form_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Padding interno
        form_content = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_content.pack(fill="both", expand=True, padx=30, pady=30)

        # ID del Paciente
        self._create_field(form_content, "ID del Paciente *", "patient_id", 0,
                          placeholder="Ej: P001")

        # Nombre
        self._create_field(form_content, "Nombre Completo *", "name", 1,
                          placeholder="Ej: Juan Pérez")

        # Frame para edad y sexo (en la misma fila)
        row2_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        row2_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        row2_frame.grid_columnconfigure((0, 1), weight=1)

        # Edad
        age_frame = ctk.CTkFrame(row2_frame, fg_color="transparent")
        age_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        age_label = ctk.CTkLabel(age_frame, text="Edad (años) *",
                                font=ctk.CTkFont(size=FONTS["size_normal"]),
                                text_color=COLORS["text_primary"])
        age_label.pack(anchor="w", pady=(0, 5))

        self.age_entry = ctk.CTkEntry(age_frame, placeholder_text="30")
        self.age_entry.pack(fill="x")

        # Sexo
        sex_frame = ctk.CTkFrame(row2_frame, fg_color="transparent")
        sex_frame.grid(row=0, column=1, sticky="ew")

        sex_label = ctk.CTkLabel(sex_frame, text="Sexo *",
                                font=ctk.CTkFont(size=FONTS["size_normal"]),
                                text_color=COLORS["text_primary"])
        sex_label.pack(anchor="w", pady=(0, 5))

        self.sex_combo = ctk.CTkComboBox(
            sex_frame,
            values=["Masculino", "Femenino", "Otro"],
            state="readonly"
        )
        self.sex_combo.set("Masculino")
        self.sex_combo.pack(fill="x")

        # Frame para masa y altura (en la misma fila)
        row3_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        row3_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)
        row3_frame.grid_columnconfigure((0, 1), weight=1)

        # Masa
        mass_frame = ctk.CTkFrame(row3_frame, fg_color="transparent")
        mass_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        mass_label = ctk.CTkLabel(mass_frame, text="Masa (kg) *",
                                 font=ctk.CTkFont(size=FONTS["size_normal"]),
                                 text_color=COLORS["text_primary"])
        mass_label.pack(anchor="w", pady=(0, 5))

        self.mass_entry = ctk.CTkEntry(mass_frame, placeholder_text="70.0")
        self.mass_entry.pack(fill="x")

        # Altura
        height_frame = ctk.CTkFrame(row3_frame, fg_color="transparent")
        height_frame.grid(row=0, column=1, sticky="ew")

        height_label = ctk.CTkLabel(height_frame, text="Altura (m) *",
                                   font=ctk.CTkFont(size=FONTS["size_normal"]),
                                   text_color=COLORS["text_primary"])
        height_label.pack(anchor="w", pady=(0, 5))

        self.height_entry = ctk.CTkEntry(height_frame, placeholder_text="1.75")
        self.height_entry.pack(fill="x")

        # Extremidad afectada
        limb_label = ctk.CTkLabel(form_content, text="Extremidad Afectada",
                                 font=ctk.CTkFont(size=FONTS["size_normal"]),
                                 text_color=COLORS["text_primary"])
        limb_label.grid(row=4, column=0, sticky="w", pady=(10, 5))

        self.limb_combo = ctk.CTkComboBox(
            form_content,
            values=["Derecha", "Izquierda", "Ambas", "Ninguna"],
            state="readonly"
        )
        self.limb_combo.set("Derecha")
        self.limb_combo.grid(row=4, column=1, sticky="ew", pady=(10, 5))

        # Diagnóstico
        diag_label = ctk.CTkLabel(form_content, text="Diagnóstico",
                                 font=ctk.CTkFont(size=FONTS["size_normal"]),
                                 text_color=COLORS["text_primary"])
        diag_label.grid(row=5, column=0, sticky="w", pady=(10, 5))

        self.diagnosis_entry = ctk.CTkEntry(form_content,
                                           placeholder_text="Ej: Dolor de rodilla, condromalacia")
        self.diagnosis_entry.grid(row=5, column=1, sticky="ew", pady=(10, 5))

        # Notas
        notes_label = ctk.CTkLabel(form_content, text="Notas Adicionales",
                                   font=ctk.CTkFont(size=FONTS["size_normal"]),
                                   text_color=COLORS["text_primary"])
        notes_label.grid(row=6, column=0, sticky="nw", pady=(10, 5))

        self.notes_text = ctk.CTkTextbox(form_content, height=80)
        self.notes_text.grid(row=6, column=1, sticky="ew", pady=(10, 5))

        # Configurar grid
        form_content.grid_columnconfigure(1, weight=1)

        # Frame de información calculada
        info_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["bg_secondary"], corner_radius=12)
        info_frame.pack(fill="x", pady=(0, 20))

        info_content = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_content.pack(fill="x", padx=30, pady=20)

        # BMI calculado
        self.bmi_label = ctk.CTkLabel(
            info_content,
            text="BMI: -- kg/m²",
            font=ctk.CTkFont(size=FONTS["size_normal"]),
            text_color=COLORS["text_secondary"]
        )
        self.bmi_label.pack(side="left", padx=(0, 20))

        # Peso corporal en Newtons
        self.weight_label = ctk.CTkLabel(
            info_content,
            text="Peso: -- N",
            font=ctk.CTkFont(size=FONTS["size_normal"]),
            text_color=COLORS["text_secondary"]
        )
        self.weight_label.pack(side="left")

        # Botones de acción
        button_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        button_frame.pack(fill="x")

        self.save_button = ctk.CTkButton(
            button_frame,
            text="Guardar Paciente",
            command=self._save_patient,
            height=40,
            font=ctk.CTkFont(size=FONTS["size_normal"], weight=FONTS["weight_bold"]),
            fg_color=COLORS["accent_primary"],
            hover_color="#00bd98"
        )
        self.save_button.pack(side="right", padx=(10, 0))

        clear_button = ctk.CTkButton(
            button_frame,
            text="Limpiar Formulario",
            command=self._clear_form,
            height=40,
            font=ctk.CTkFont(size=FONTS["size_normal"]),
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["bg_hover"]
        )
        clear_button.pack(side="right")

        # Vincular eventos para calcular BMI automáticamente
        self.mass_entry.bind("<KeyRelease>", self._update_calculated_info)
        self.height_entry.bind("<KeyRelease>", self._update_calculated_info)

    def _create_field(self, parent, label_text, var_name, row, placeholder=""):
        """
        Crea un campo de formulario.

        Args:
            parent: Widget padre
            label_text: Texto de la etiqueta
            var_name: Nombre de la variable
            row: Fila del grid
            placeholder: Texto placeholder
        """
        label = ctk.CTkLabel(parent, text=label_text,
                           font=ctk.CTkFont(size=FONTS["size_normal"]),
                           text_color=COLORS["text_primary"])
        label.grid(row=row, column=0, sticky="w", pady=(10, 5))

        entry = ctk.CTkEntry(parent, placeholder_text=placeholder)
        entry.grid(row=row, column=1, sticky="ew", pady=(10, 5))

        setattr(self, f"{var_name}_entry", entry)

    def _update_calculated_info(self, event=None):
        """Actualiza información calculada (BMI, peso)."""
        try:
            mass = float(self.mass_entry.get())
            height = float(self.height_entry.get())

            if mass > 0 and height > 0:
                # Calcular BMI
                bmi = mass / (height ** 2)
                self.bmi_label.configure(text=f"BMI: {bmi:.1f} kg/m²")

                # Calcular peso en Newtons
                weight_n = mass * 9.81
                self.weight_label.configure(text=f"Peso: {weight_n:.1f} N")
        except ValueError:
            self.bmi_label.configure(text="BMI: -- kg/m²")
            self.weight_label.configure(text="Peso: -- N")

    def _save_patient(self):
        """Guarda la información del paciente."""
        try:
            # Obtener valores
            patient_id = self.patient_id_entry.get().strip()
            name = self.name_entry.get().strip()
            age_str = self.age_entry.get().strip()
            mass_str = self.mass_entry.get().strip()
            height_str = self.height_entry.get().strip()

            # Validar ID
            valid, error = validate_patient_id(patient_id)
            if not valid:
                self._show_error(error)
                return

            # Validar edad, masa, altura
            try:
                age = int(age_str)
                mass = float(mass_str)
                height = float(height_str)
            except ValueError:
                self._show_error("Edad, masa y altura deben ser números válidos")
                return

            # Validar datos
            valid, error = validate_patient_data(name, age, mass, height)
            if not valid:
                self._show_error(error)
                return

            # Convertir sexo
            sex_map = {"Masculino": Sex.MALE, "Femenino": Sex.FEMALE, "Otro": Sex.OTHER}
            sex = sex_map[self.sex_combo.get()]

            # Convertir extremidad afectada
            limb_map = {
                "Derecha": AffectedLimb.RIGHT,
                "Izquierda": AffectedLimb.LEFT,
                "Ambas": AffectedLimb.BOTH,
                "Ninguna": AffectedLimb.NONE
            }
            affected_limb = limb_map[self.limb_combo.get()]

            # Crear paciente
            patient = Patient(
                patient_id=patient_id,
                name=name,
                age=age,
                mass=mass,
                height=height,
                sex=sex,
                affected_limb=affected_limb,
                diagnosis=self.diagnosis_entry.get().strip(),
                notes=self.notes_text.get("1.0", "end-1c").strip()
            )

            self.current_patient = patient

            logger.info(f"Paciente guardado: {patient.patient_id} - {patient.name}")

            # Llamar callback si existe
            if self.on_patient_saved:
                self.on_patient_saved(patient)

            self._show_success("Paciente guardado correctamente")

        except Exception as e:
            logger.error(f"Error guardando paciente: {str(e)}", exc_info=True)
            self._show_error(f"Error al guardar: {str(e)}")

    def _clear_form(self):
        """Limpia todos los campos del formulario."""
        self.patient_id_entry.delete(0, "end")
        self.name_entry.delete(0, "end")
        self.age_entry.delete(0, "end")
        self.mass_entry.delete(0, "end")
        self.height_entry.delete(0, "end")
        self.sex_combo.set("Masculino")
        self.limb_combo.set("Derecha")
        self.diagnosis_entry.delete(0, "end")
        self.notes_text.delete("1.0", "end")

        self.bmi_label.configure(text="BMI: -- kg/m²")
        self.weight_label.configure(text="Peso: -- N")

        self.current_patient = None

        logger.info("Formulario de paciente limpiado")

    def load_patient(self, patient: Patient):
        """
        Carga información de un paciente en el formulario.

        Args:
            patient: Paciente a cargar
        """
        self._clear_form()

        self.patient_id_entry.insert(0, patient.patient_id)
        self.name_entry.insert(0, patient.name)
        self.age_entry.insert(0, str(patient.age))
        self.mass_entry.insert(0, str(patient.mass))
        self.height_entry.insert(0, str(patient.height))

        # Sexo
        sex_map_inv = {Sex.MALE: "Masculino", Sex.FEMALE: "Femenino", Sex.OTHER: "Otro"}
        self.sex_combo.set(sex_map_inv[patient.sex])

        # Extremidad
        limb_map_inv = {
            AffectedLimb.RIGHT: "Derecha",
            AffectedLimb.LEFT: "Izquierda",
            AffectedLimb.BOTH: "Ambas",
            AffectedLimb.NONE: "Ninguna"
        }
        self.limb_combo.set(limb_map_inv[patient.affected_limb])

        self.diagnosis_entry.insert(0, patient.diagnosis)
        self.notes_text.insert("1.0", patient.notes)

        self.current_patient = patient

        self._update_calculated_info()

        logger.info(f"Paciente cargado: {patient.patient_id}")

    def _show_error(self, message: str):
        """Muestra mensaje de error (placeholder)."""
        # Esto se conectará con AlertManager
        logger.warning(f"Error en formulario de paciente: {message}")
        print(f"ERROR: {message}")

    def _show_success(self, message: str):
        """Muestra mensaje de éxito (placeholder)."""
        logger.info(f"Éxito en formulario de paciente: {message}")
        print(f"ÉXITO: {message}")
