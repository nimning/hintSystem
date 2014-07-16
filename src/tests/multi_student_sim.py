import student_sim
from multiprocessing import Process
from multiprocessing import Pool

user_count = 10
def main():
    pool = Pool(processes=4)
    results = []
    for i in range(1,1+user_count):
        r = pool.apply_async(student_sim.simulate_student, ['hw.yaml', '192.168.33.10',
                                                        'UCSD_CSE103', 0.1,
                                                        "student{0}".format(i),
                                                        "{0}".format(50000+i)] )
        results.append(r)
    for r in results:
        r.wait()
        print r.get()
        print r.successful()
if __name__ == '__main__':
    main()
