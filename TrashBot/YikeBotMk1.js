const Discord = require('discord.js');

const client = new Discord.Client();
const RoleName = 'Yikes:';

client.on('ready', () => {
  console.log('Bot Online');
});

client.login('NjE0Mjg0NzAyOTk5OTA0MjU5.XWC7uQ.iPveiNrThNCLY_-GKfFh5b-XW0Q');

client.on('message', message =>
{
	if(message.content.substring(0,1) === '\\')
	{
		var args = message.content.substring(1).split(' ');
		if(args.length == 2 && args[0] == 'yike')
		{
			message.channel.send(args[1] + ".... yikes\n:yike:");
			
			var member = message.member;
			var roles = member.roles;
			var done;
			
			let cur = roles.find(role => role.name.split(' ')[0] == RoleName)
				var name = cur.name.split(' ');
				if(name.length == 2 && name[0] == RoleName)
				{
					var num = parseInt(name[1]);
					cur.name = RoleName + " " + (num + 1);
					member.addRole(cur);
					done = true;
				}
		}
		
		if(!done)
		{
			console.log('No Role Found');
		}
	}
});

