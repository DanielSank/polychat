use std::io::Write;
use std::net::{TcpListener, TcpStream};
use std::thread;


struct Server {
    connections: 
}

impl Server {
    fn data_received(&self, s: String) {
        for connection in self.connections {
            connection.

fn get_listener(host: &str) -> TcpListener {
    let maybe_listener = TcpListener::bind(host);
    match maybe_listener {
        Err(_)=> {
            println!("Failed to listen");
            std::process::exit(0);
        },
        Ok(x) => x
    }
}


fn handle_connection(mut stream: TcpStream) {
    let result = stream.write(b"Hello, world!");
    
}


fn main() {
    let listener = get_listener("127.0.0.1:1234");
    println!("Listening on 1234...");
    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                thread::spawn(move || {handle_connection(stream)});
            },
            Err(_) => {
                println!("Failed to accept");
                std::process::exit(0);
            }
        }
    }
}


/*
thread::spawn(|| {
    let mut stream = stream.unwrap();
    stream.write(b"Hello, world!\r\n").unwrap();
*/
