import simpy
import random
import statistics
import matplotlib.pyplot as plt

# -----------------------------
# FUNCIÓN DE SIMULACIÓN
# -----------------------------
def simular(total_processes, interval, ram_capacity=100, cpu_speed=3, cpu_count=1):
    
    random.seed(1)
    times = []

    # Proceso individual
    def proceso(env, ram, cpu):
        start_time = env.now
        memoria = random.randint(1, 10)
        instrucciones = random.randint(1, 10)

        yield ram.get(memoria)

        while instrucciones > 0:
            with cpu.request() as req:
                yield req
                yield env.timeout(1)

                ejecutadas = min(cpu_speed, instrucciones)
                instrucciones -= ejecutadas

            if instrucciones > 0:
                if random.randint(1, 21) == 1:
                    yield env.timeout(1)

        yield ram.put(memoria)
        times.append(env.now - start_time)

    # Generador de procesos
    def generador(env, total, ram, cpu):
        for _ in range(total):
            env.process(proceso(env, ram, cpu))
            yield env.timeout(random.expovariate(1.0 / interval))

    env = simpy.Environment()
    ram = simpy.Container(env, init=ram_capacity, capacity=ram_capacity)
    cpu = simpy.Resource(env, capacity=cpu_count)

    env.process(generador(env, total_processes, ram, cpu))
    env.run()

    return statistics.mean(times) , statistics.stdev(times)


# -----------------------------
# GENERACIÓN DE GRÁFICAS
# -----------------------------

process_counts = [25, 50, 100, 150, 200]
intervals = [10, 5, 1]

configuraciones = [
    ("Normal", 100, 3, 1),
    ("RAM_200", 200, 3, 1),
    ("CPU_Rapido", 100, 6, 1),
    ("2_CPUs", 100, 3, 2)
]

for interval in intervals:

    plt.figure()
    print("\n==============================")
    print(f"INTERVALO = {interval}")
    print("==============================")

    for nombre, ram_cap, cpu_spd, cpu_cnt in configuraciones:

        means = []

        print(f"\nConfiguración: {nombre}")

        for p in process_counts:

            promedio, desviacion = simular(
                p,
                interval,
                ram_capacity=ram_cap,
                cpu_speed=cpu_spd,
                cpu_count=cpu_cnt
            )

            means.append(promedio)

            print(f"Procesos: {p}")
            print(f"  Promedio: {promedio:.4f}")
            print(f"  Desviación: {desviacion:.4f}")

        plt.plot(process_counts, means, label=nombre)

    plt.xlabel("Número de procesos")
    plt.ylabel("Tiempo promedio")
    plt.title(f"Comparación de configuraciones | Intervalo = {interval}")
    plt.legend()
    plt.show()