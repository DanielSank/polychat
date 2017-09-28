import io.netty.bootstrap.ServerBootstrap
import io.netty.channel._
import io.netty.channel.nio.NioEventLoopGroup
import io.netty.channel.socket.SocketChannel
import io.netty.channel.socket.nio.NioServerSocketChannel
import scala.concurrent.ExecutionContext
import scala.util.{Failure, Success, Try}

class Listener(port: Int, hub: Hub)(implicit ec: ExecutionContext) {
  val bossGroup = new NioEventLoopGroup(1)
  val workerGroup = new NioEventLoopGroup()

  class ChatChannelInitializer extends ChannelInitializer[SocketChannel] {
    override def initChannel(ch: SocketChannel): Unit = {
      ch.pipeline.addLast("messageCodec", new MessageCodec(hub))
    }
  }

  val channel = try {
    val b = new ServerBootstrap()
    b.group(bossGroup, workerGroup)
     .channel(classOf[NioServerSocketChannel])
     .childOption[java.lang.Boolean](ChannelOption.TCP_NODELAY, true)
     .childOption[java.lang.Boolean](ChannelOption.SO_KEEPALIVE, true)
     .childHandler(new ChatChannelInitializer)

    // Bind and start to accept incoming connections.
    b.bind(port).sync().channel
  } catch {
    case e: Exception =>
      stop()
      throw e
  }
  
  def stop(): Unit = {
    shutdown(channel)
  }

  private def shutdown(channel: Channel): Unit = {
    try {
      channel.close()
      channel.closeFuture.sync()
    } finally {
      workerGroup.shutdownGracefully()
      bossGroup.shutdownGracefully()
    }
  }
}
