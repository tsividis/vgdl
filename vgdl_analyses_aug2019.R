#### MAIN FIGURE ###
main_plot_agent_types = c('rainbow', 'DDQN 100k', 'EMPA')
s = filter(human_normed_data, agent_type=='EMPA')
ordered_names = s[order(log(s$human_normed_composite_ratio)),]$formatted_game_name
p = ggplot()+
  geom_bar(data=filter(human_normed_data, agent_type%in%main_plot_agent_types & agent_type=='EMPA', log(human_normed_composite_ratio, 10)>-3),
           aes(x=formatted_game_name, y=log(human_normed_composite_ratio), fill=as.factor(agent_type)), stat='identity', position='dodge')+
  geom_point(data=filter(human_normed_data, agent_type%in%main_plot_agent_types & 
                           ((agent_type == 'EMPA'  & !(log(human_normed_composite_ratio, 10)>-3)) | agent_type%in%c('DDQN 100k', 'rainbow 50k', 'rainbow 150k', 'rainbow 250k')),
             aes(x=formatted_game_name, y=log(human_normed_composite_ratio), color=agent_type), stat='identity', position='dodge', shape='|', size=3, stroke=2)+
  scale_x_discrete(limits=ordered_names)+
  # theme(legend.position="none")+
  colorScale+
  theme(axis.text.x = element_text(angle = 90, hjust = 1),legend.position='none')+ylab("Human-normed Efficiency")+xlab('Game name')+ylim(-10,10)
tickmarks = c(1e-7,1e-6, 1e-5,1e-4,1e-3,1e-2,1e-1,1e0,1e1,1e2,1e3,1e4, 1e5)
logtickmarks=(log(tickmarks))
tickmarks = c('0 (fail)', 1e-6, 1e-5,1e-4,1e-3,1e-2,1e-1,1e0,1e1,1e2,1e3,1e4, 1e5)
p=p+coord_flip()+scale_y_continuous(breaks=logtickmarks,labels=tickmarks)
p + scale_fill_manual(values=colors,name="Model",
                      breaks=c("EMPA", "DDQN 100k"),
                      labels=c("EMPA", "DDQN")) + scale_color_manual(values=colors,name="Model",
                                                                     breaks=c("EMPA", "DDQN 100k"),
                                                                     labels=c("EMPA", "DDQN"))