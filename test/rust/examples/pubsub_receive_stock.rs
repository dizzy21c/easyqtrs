// Port of https://www.rabbitmq.com/tutorials/tutorial-three-python.html. Start this
// example in one shell, then run the pubsub_emit_log example in another.

// extern crate crossbeam_utils;
// extern crate ndarray;

use amiquip::{
    Connection, ConsumerMessage, ConsumerOptions, ExchangeDeclareOptions, ExchangeType, FieldTable,
    QueueDeclareOptions, Result,
};
// use crossbeam_channel::bounded;
// use crossbeam_channel::{Receiver, Sender};
// use ndarray::array;
// use serde::{Deserialize, Serialize};
// use serde_json::json;
// use serde_json::value::Value;

// // extern crate crossbeam_utils;
// // extern crate ndarray;
// use crate::dataframe::DataCell;

// mod dataframe;

// use std::thread;


fn main() -> Result<()> {
    env_logger::init();

    // Open connection.
    let mut connection = Connection::insecure_open("amqp://admin:admin@localhost:5672")?;

    // Open a channel - None says let the library choose the channel ID.
    let channel = connection.open_channel(None)?;

    // Declare the fanout exchange we will bind to.
    let exchange = channel.exchange_declare(
        // ExchangeType::Fanout,
        // "stocktransaction",
        ExchangeType::Direct,
        "stockcn",
        // "realtime_000735",
        ExchangeDeclareOptions::default(),
    )?;

    // Declare the exclusive, server-named queue we will use to consume.
    let queue = channel.queue_declare(
        "",
        QueueDeclareOptions {
            exclusive: true,
            ..QueueDeclareOptions::default()
        },
    )?;
    println!("created exclusive queue {}", queue.name());

    // Bind our queue to the logs exchange.
    let rk = "000735";
    queue.bind(&exchange, rk, FieldTable::new())?;

    // Start a consumer. Use no_ack: true so the server doesn't wait for us to ack
    // the messages it sends us.
    let consumer = queue.consume(ConsumerOptions {
        no_ack: true,
        ..ConsumerOptions::default()
    })?;
    println!("Waiting for logs. Press Ctrl-C to exit.");

    for (i, message) in consumer.receiver().iter().enumerate() {
        match message {
            ConsumerMessage::Delivery(delivery) => {
                let body = String::from_utf8_lossy(&delivery.body);
                println!("({:>3}) {}", i, body);
            }
            other => {
                println!("Consumer ended: {:?}", other);
                break;
            }
        }
    }

    connection.close()
}
