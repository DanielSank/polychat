import io.netty.buffer.ByteBuf
import io.netty.channel._
import io.netty.handler.codec._
import java.nio.charset.StandardCharsets.UTF_8
//import io.netty.util.AttributeKey
import java.util.{List => JList}



class MessageCodec(hub: Hub) extends ByteToMessageCodec[String] {

  val NEWLINE = '\n'.toByte

  override def channelActive(ctx: ChannelHandlerContext): Unit = {
    super.channelActive(ctx)
    hub.registerChannel(ctx.channel)
  }

  protected override def decode(ctx: ChannelHandlerContext, in: ByteBuf, outList: JList[AnyRef]): Unit = {

    val nextTerminatorIndex = in.indexOf(0, in.capacity(), NEWLINE)
    if (nextTerminatorIndex == -1) {return}
    val data = in.readSlice(nextTerminatorIndex + 1)
    hub.messageReceived(data.toString(UTF_8))
  }

  override def encode(ctx: ChannelHandlerContext, message: String, out: ByteBuf): Unit = {
    out.writeBytes(message.getBytes(UTF_8))
  }
}
