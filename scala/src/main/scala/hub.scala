import io.netty.channel._

class Hub {
  private var channels: List[Channel] = Nil

  def registerChannel(ch: Channel): Unit = {
    channels = ch :: this.channels
  }

  // When a message comes in, send it back out over all channels.
  def messageReceived(message: String): Unit = {
    for (ch <- channels) {
      ch.writeAndFlush(message)
    }
  }
}
