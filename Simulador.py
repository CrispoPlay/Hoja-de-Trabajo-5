#nombre: Cristian Orellaan
import simpy
import random
import statistics

# -----------------------------
# PARÁMETROS FIJOS
# -----------------------------
RANDOM_SEED = 1
RAM_CAPACITY = 100      # Memoria total disponible
CPU_SPEED = 3           # Instrucciones por unidad de tiempo
INTERVAL = 10           # Tiempo promedio entre llegadas
TOTAL_PROCESSES = 25    # Cantidad de procesos a simular

random.seed(RANDOM_SEED)

# Lista para guardar tiempos finales
times = []

# -----------------------------
# PROCESO
# -----------------------------
def proceso(env, name, ram, cpu):
    
    start_time = env.now  # Momento en que llega
    
    memoria = random.randint(1, 10)       # Memoria que necesita
    instrucciones = random.randint(1, 10) # Instrucciones totales

    # Solicita memoria RAM
    yield ram.get(memoria)

    # Mientras tenga instrucciones pendientes
    while instrucciones > 0:
        with cpu.request() as req:
            yield req
            yield env.timeout(1)  # Usa CPU por 1 unidad de tiempo

            # Ejecuta hasta CPU_SPEED instrucciones
            ejecutadas = min(CPU_SPEED, instrucciones)
            instrucciones -= ejecutadas

        # Posible I/O
        if instrucciones > 0:
            if random.randint(1, 21) == 1:
                yield env.timeout(1)

    # Devuelve memoria
    yield ram.put(memoria)

    # Guarda tiempo total en el sistema
    times.append(env.now - start_time)


# -----------------------------
# GENERADOR DE PROCESOS
# -----------------------------
def generador(env, total, ram, cpu):
    for i in range(total):
        env.process(proceso(env, f"Proceso {i}", ram, cpu))
        yield env.timeout(random.expovariate(1.0 / INTERVAL))


# -----------------------------
# FUNCIÓN PRINCIPAL
# -----------------------------
def simular():

    env = simpy.Environment()

    ram = simpy.Container(env, init=RAM_CAPACITY, capacity=RAM_CAPACITY)
    cpu = simpy.Resource(env, capacity=1)

    env.process(generador(env, TOTAL_PROCESSES, ram, cpu))
    env.run()

    promedio = statistics.mean(times)
    desviacion = statistics.stdev(times)

    print("Tiempo promedio:", promedio)
    print("Desviación estándar:", desviacion)


# Ejecutar simulación
simular()