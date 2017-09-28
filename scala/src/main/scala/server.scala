import scala.concurrent.ExecutionContext.Implicits.global

class CentralNode(port: Int) {
  val hub: Hub = new Hub()

  // start listening for incoming network connections
  val listener = new Listener(port, hub)

  def stop() {
    listener.stop()
  }
}

object Manager {
  def main(args: Array[String]) {
    val centralNode = new CentralNode(8033)
  }
}
