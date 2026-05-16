import psutil
import time
import collections
import statistics

class OptimizationEngine:
    def __init__(self, history_size=60, stress_multiplier=1.5):
        """
        :param history_size: Cantidad de muestras para la línea base (ej. 1 min a 1 muestra/seg)
        :param stress_multiplier: Multiplicador sobre la media para considerar estado de estrés
        """
        self.cpu_history = collections.deque(maxlen=history_size)
        self.ram_history = collections.deque(maxlen=history_size)
        self.stress_multiplier = stress_multiplier
        self.current_health_score = 100.0

    def collect_metrics(self):
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        self.cpu_history.append(cpu)
        self.ram_history.append(ram)
        return cpu, ram

    def calculate_health_score(self, cpu, ram):
        # Lógica de penalización: mayor uso de recursos reduce la puntuación
        cpu_penalty = max(0, cpu - 50) * 0.5  # Penaliza si CPU > 50%
        ram_penalty = max(0, ram - 70) * 0.8  # Penaliza más duro si RAM > 70%
        score = 100.0 - (cpu_penalty + ram_penalty)
        return max(0.0, min(100.0, score))

    def evaluate_stress_state(self):
        if len(self.cpu_history) < 10:
            return False, "Recopilando línea base..."

        current_cpu, current_ram = self.collect_metrics()
        
        # Umbral dinámico basado en la media histórica reciente
        cpu_baseline = statistics.mean(self.cpu_history)
        ram_baseline = statistics.mean(self.ram_history)
        
        self.current_health_score = self.calculate_health_score(current_cpu, current_ram)
        
        is_stressed = False
        reasons = []

        if current_cpu > (cpu_baseline * self.stress_multiplier) and current_cpu > 60:
            is_stressed = True
            reasons.append(f"Pico de CPU anómalo: {current_cpu}%")
            
        if current_ram > (ram_baseline * 1.2) and current_ram > 85:
            is_stressed = True
            reasons.append(f"Saturación de RAM crítica: {current_ram}%")

        return is_stressed, reasons

    def tick(self):
        is_stressed, info = self.evaluate_stress_state()
        return {
            "health_score": round(self.current_health_score, 1),
            "is_stressed": is_stressed,
            "info": info
        }

if __name__ == "__main__":
    engine = OptimizationEngine()
    print("Iniciando NEX-PULSE AI OPTIMIZER Core Engine...")
    for _ in range(5):
        status = engine.tick()
        print(f"Health: {status['health_score']} | Stressed: {status['is_stressed']} | {status['info']}")
        time.sleep(1)
