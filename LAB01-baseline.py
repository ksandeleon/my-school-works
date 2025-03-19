import simpy
import random
import numpy

env = simpy.Environment()

cashier_count = 2
barista_count = 4
customer_count = 100

cashier = simpy.Resource(env, capacity=cashier_count)
barista = simpy.Resource(env, capacity=barista_count)

menu = {
    1: ["Regular Coffee", 10, 15],
    2: ["Latte", 30, 45],
    3: ["Mocha", 30, 45],
    4: ["Cold Brew", 10, 20],
    5: ["Frappe", 50, 70],
    6: ["Espresso", 20, 35]
}

payment_options = {
    1: ["Cash", 15, 30],
    2: ["Card", 10, 20]
}

payment_wait_time = []
payment_time = []
order_wait_time = []
order_time = []


def generate_customer(env, cashier, barista):
    for i in range(customer_count):
        yield env.timeout(random.randint(1, 20))
        env.process(customer(env, i, cashier, barista))


def customer(env, name, cashier, barista):
    print("Customer %s arrived at time %.1f" % (name, env.now))

    with cashier.request() as req:
        start_cq = env.now
        yield req
        payment_wait_time.append(env.now - start_cq)

        menu_item = random.randint(1, 6)
        payment_type = random.randint(1, 2)
        time_to_order = random.randint(payment_options[payment_type][1], payment_options[payment_type][2])
        payment_name = payment_options[payment_type][0]

        yield env.timeout(time_to_order)
        print(">>> Customer %s finished paying by %s in %.1f seconds" % (name, payment_name, env.now - start_cq))
        payment_time.append(env.now - start_cq)

    with barista.request() as req:
        start_bq = env.now
        yield req
        order_wait_time.append(env.now - start_bq)

        time_to_prepare = random.randint(menu[menu_item][1], menu[menu_item][2])
        item_name = menu[menu_item][0]

        yield env.timeout(time_to_prepare)
        print(">> >> >> Customer %s served %s in %.1f seconds" % (name, item_name, env.now - start_cq))
        order_time.append(env.now - start_cq)


env.process(generate_customer(env, cashier, barista))

print("WITH %s CASHIERS AND %s BARISTAS AND %s SERIALLY ARRIVING CUSTOMERS..." % (cashier_count, barista_count, customer_count))

env.run()

print("Average wait time in payment queue: %.1f seconds." % (numpy.mean(payment_wait_time)))
print("Average time until making the payment: %.1f seconds." % (numpy.mean(payment_time)))
print("Average wait time in order queue: %.1f seconds." % (numpy.mean(order_wait_time)))
print("Average time until order is serviced: %.1f seconds." % (numpy.mean(order_time)))
