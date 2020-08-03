setwd('/Users/pedrotsividis/Projects/atari/vgdl')
## Once you set it, you can load the workspace using load(".RData") !

## gameplay data
EMPA_dates = list('mar28')
refactor_dates = list('refactor_feb13')
humandatapaths = list.files(paste(getwd(),'/data_files/humandata', sep=''))

## Load helper functions
source(paste(getwd(), '/TBRL_functions.R', sep=''))

## Load data. These next few lines take a long time.
humandata = load_reward_data('human', NA)
EMPAdata = load_reward_data('EMPA', EMPA_dates)
rEMPAdata = load_reward_data('EMPA', refactor_dates)
rEMPAdata$agent_type = as.factor('EMPA_refactor')

##Load subjective game ratings
ratings = load_ratings()

## Remove subject-game pairs where the subject said they'd played the game before.
played_before = filter(ratings, played.before=='Yes')
for (game in unique(played_before$gameName)){
  for (subject in unique(filter(played_before, gameName==game)$subject)){
    humandata = filter(humandata, !((game_name==game) & (subject_ID==subject)))
  }
}

## Find all (subject, game, level) tuples where the subject was forced to play a level more than once.
## (this is slow)
excluded_subjects = data.frame(game_name=as.character(), subject_ID=as.character(), level=as.numeric())
for (game in unique(humandata$game_name)){
  human_game_data = filter(humandata, game_name==game)
  for (subject in unique(humandata$subject_ID)){
    subject_data = filter(humandata, subject_ID==subject)
    for (level in unique(subject_data$level_number)){
      if (length(unique(filter(subject_data, level_number==level)$cumulative_wins))>2){
        excluded_subjects = rbind(excluded_subjects, data.frame(game_name=game, subject_ID=subject, level_number=level))
      }
    }
  }
}
## Remove game-subject pairs where the subject played a given level in a game more than once 
## (this only happened a few times)
for (i in 1:length(excluded_subjects$game_name)){
  row = excluded_subjects[i,]
  game = row$game_name
  subject = row$subject_ID
  humandata = filter(humandata, !((game_name==as.character(game))&(subject_ID==as.character(subject))))
}



alldata = rbind(humandata, EMPAdata, rEMPAdata)
#refactor_human_normed = make_human_normed_data(rbind(humandata, rEMPAdata))
human_normed_data = make_human_normed_data(alldata)

colors = c('steelblue1', 'purple1', 'palegreen3')
names(colors) = c('EMPA', 'EMPA_refactor', 'human')

# colors = c('steelblue1', 'slategray2',
#            'slateblue1', 'slateblue4', 'mediumpurple1', 'purple1',
#            'firebrick2', 'magenta3',
#            'palegreen3',
#            'gray50', 'gray65', 'gray80',
#            'orange3', 'tomato3', 'red3', 'red3',
#            'goldenrod1', 'goldenrod2', 'goldenrod3', 'darkslategray2', 'darkolivegreen3')
# names(colors)=c('EMPA', 'EMPA fail',
#                 'e-greedy 1k', 'e-greedy 2k', 'e-greedy 1k DS', 'e-greedy 2k DS',
#                 'random policy', 'random',
#                 'human',
#                 'DDQN 100k', 'DDQN 10k', 'DDQN 1k',
#                 'rainbow 250k', 'rainbow 150k', 'rainbow 50k', 'rainbow',
#                 'no goal gradient', 'no subgoals', 'no subgoals + no gradient', 'no IW', 'no subgoals + no gradient + no IW')
# 

### Learning curve plots
## plotting all agents/models
# agents_to_plot = c('human', 'EMPA', 'EMPA_refactor')
agents_to_plot=c('EMPA_refactor')
# games_to_plot = c('bait', 'zelda', 'butterflies', 'avoidgeorge','frogs','plaqueattack')
games_to_plot = unique(rEMPAdata$game_name)
games_in_order = unique(rEMPAdata$game_name)[order(unique(rEMPAdata$game_name))]
plots = list()
for (k in 1:length(games_to_plot)){
# for (k in 1:length(games_in_order)){
  # game = games_in_order[k]
  game = games_to_plot[k]

  max_x = 10000
  
  ## used for interpolating data points to sparse DDQN data
  if(max_x<5000){
    step_size=5
  }else if(max_x<100000){
    step_size=100
  }else if(max_x<1000000){
    step_size=1000
  }else{
    step_size=10000
  }
  
  d = filter(alldata, game_name==as.character(game), agent_type %in% agents_to_plot)
  ### assign correct colors to each subject ID
  plotcolors = c()
  for (agent in agents_to_plot){
    agent_subjects = unique(filter(d, agent_type==agent)$subject_ID)
    agent_color = colors[agent]
    colorlist = rep(agent_color, length(agent_subjects))
    names(colorlist) = agent_subjects
    plotcolors = c(plotcolors, colorlist)
  }
  
  if (game%in%levels(excluded_subjects)){
    es = filter(excluded_subjects, game_name==game)
    subjects_to_exclude = unique(es$subject_ID)
  }else{
    subjects_to_exclude = c()
  }

  d = filter(d, !(subject_ID%in%subjects_to_exclude))


  if (game %in% c('antagonist', 'antagonist_1', 'antagonist_2', 'bees_and_birds', 'bees_and_birds_1', 
                  'closing_gates', 'closing_gates_1', 'corridor', 'corridor_1', 
                  'helper', 'helper_1', 'helper_2', 'preconditions', 'preconditions_1', 'preconditions_2',
                  'push_boulders', 'push_boulders_1', 'push_boulders_2', 'relational', 'relational_1', 'relational_2',
                  'surprise', 'surprise_1', 'surprise_2')){
    level_max = 4
  }else if (game %in% c('ee', 'ee_1', 'ee_2', 'ee_3')){
    level_max = 6
  }else{
    level_max = 5
  }
  ## Add data points for every 'step_size' DDQN time-step, since we can afford to do this and know what the data points are
  ## (as we recorded end-of-episode data and cumulative_wins definitionally don't change before then)
  if (max_x<1000000){
  replacement_subjects = data.frame(game_name=as.character(), agent_type=as.character(), long_agent_type=as.character(), subject_ID=as.character(),
                              modelrun_ID=as.character(), level_number=as.numeric(), cumulative_steps=as.numeric(), cumulative_wins=as.numeric(), score=as.numeric())
  clean_d=filter(d, (!grepl('DDQN', agent_type) & (!grepl('rainbow', agent_type))) )
  for (subject in unique(filter(d, (grepl('DDQN', agent_type)|(grepl('rainbow', agent_type))))$subject_ID)){
    subject_data = filter(d, subject_ID==subject, cumulative_steps<max_x)
    
    ## if we actually have subject data for the max_x cutoff we care about...
    if (length(subject_data$cumulative_steps)>0){
      subject_agent_type = subject_data$agent_type[1]
      last_steps = 0
      
      new_subject_df = data.frame(game_name=as.character(), agent_type=as.character(), long_agent_type=as.character(), subject_ID=as.character(),
                                  modelrun_ID=as.character(), level_number=as.numeric(), cumulative_steps=as.numeric(), cumulative_wins=as.numeric(), score=as.numeric())
      
      for (i in 1:length(subject_data$cumulative_steps)){ ## meaning, for each episode
        subject_row = subject_data[i,]
        if ( (last_steps<subject_row$cumulative_steps)){
          if (subject_row$cumulative_wins<level_max){## add lots of points if game is not won
            for (j in seq(last_steps, subject_row$cumulative_steps-1,step_size)){
                    row = data.frame(game_name=game, agent_type=subject_data$agent_type[1], long_agent_type=subject_data$long_agent_type[1], subject_ID=subject,
                           modelrun_ID=subject_data$modelrun_ID[1], level_number=subject_row$level_number, cumulative_steps=j, cumulative_wins=subject_row$cumulative_wins,
                           score=subject_row$score)
            new_subject_df = rbind(new_subject_df, row)
            }
          }
          else{ ## just add the last row
              row = data.frame(game_name=game, agent_type=subject_data$agent_type[1], long_agent_type=subject_data$long_agent_type[1], subject_ID=subject,
                               modelrun_ID=subject_data$modelrun_ID[1], level_number=subject_row$level_number, cumulative_steps=j, cumulative_wins=subject_row$cumulative_wins,
                               score=subject_row$score)
              new_subject_df = rbind(new_subject_df, row)    
            }
        new_subject_df = rbind(new_subject_df, subject_row)
        last_steps = subject_row$cumulative_steps
        }
      }
      ## If we haven't filled out the x range
      last_x = new_subject_df$cumulative_steps[length(new_subject_df$cumulative_steps)]
      if(last_x+step_size<max_x){
        subject_row = new_subject_df[length(new_subject_df$cumulative_steps),]
        for (j in seq(last_x+step_size, max_x, step_size)){
          row = data.frame(game_name=game, agent_type=subject_data$agent_type[1], long_agent_type=subject_data$long_agent_type[1], subject_ID=subject,
                           modelrun_ID=subject_data$modelrun_ID[1], level_number=subject_row$level_number, cumulative_steps=j, cumulative_wins=subject_row$cumulative_wins,
                           score=subject_row$score)
          new_subject_df = rbind(new_subject_df, row)
        }
      }
      replacement_subjects = rbind(replacement_subjects, new_subject_df)
    } 
    
    clean_d = rbind(clean_d, replacement_subjects) 
  }
  d = clean_d
  }
  
  d = filter(d, cumulative_steps<=max_x)
  
  ## you can only assume DDQN kept playing for max_x steps. Humans might have quit before then, and EMPA might be stuck thinking, within the allotted limit.
  no_win_subjects = c()
  for (subject in unique(d$subject_ID)){
    if (max(filter(d, subject_ID==subject, cumulative_steps<=max_x)$cumulative_wins)==0){
      no_win_subjects = c(no_win_subjects, subject)
    }
  }
  
  ### calculate kappas here:
  kappa_df = data.frame(agent_type=as.character, efficiency=as.numeric())
  for (agent in unique(d$agent_type)){
    agent_data = filter(d, agent_type==agent)
    
    level_maxes = list()
    cumulative_step_maxes = list()
    idx=1
    for (l in 1:length(unique(agent_data$subject_ID))){
      subject = unique(agent_data$subject_ID)[l]
      subjectdata = filter(agent_data, subject_ID==subject)
      if (length(subjectdata$cumulative_steps)>0){
        if(max(subjectdata$cumulative_steps)>0){
          level_maxes[[idx]] = max(subjectdata$cumulative_wins)
          cumulative_step_maxes[[idx]] = max(subjectdata$cumulative_steps)
          idx = idx+1            
        }
      }
    }
    
    ## mean vector of win numbers
    mean_wins = mean(as.numeric(as.vector(level_maxes)))
    
    ##mean of vector steps+to+win ratios (kappa)
    l_e = mean(as.numeric(as.vector(level_maxes))/as.numeric(as.vector(cumulative_step_maxes)))
    kappa_df = rbind(kappa_df, data.frame(agent_type=agent, efficiency=l_e))
  }
  
  d=transform(d, subject_ID=factor(subject_ID, levels=names(plotcolors))) ## reorder in order to plot EMPA on top, as it otherwise can get lost in the many human curves.
  max_y = level_max
  
  game_title=gsub('_',' ',game)
  if (game_title=='ee'){
    game_title='explore/exploit'
  }
  if (game_title=='ee 1'){
    game_title='explore/exploit 1'
  }
  if (game_title=='ee 2'){
    game_title='explore/exploit 2'
  }
  if (game_title=='ee 3'){
    game_title='explore/exploit 3'
  }
  p = ggplot(d ,aes(x=cumulative_steps,y=cumulative_wins, color=subject_ID, size=agent_type))+geom_point()+ 
    ggtitle(game_title)+theme(legend.position="none")+scale_color_manual(values=plotcolors)+scale_size_manual(values=c(1,1,1,1))+
    xlab('Steps taken by agent')+ylab('Levels won')+
    theme(plot.title=element_text(family='',face='plain', size=26, hjust=0.5),
          axis.text.x=element_text(size=22),
          axis.text.y=element_text(size=22),
          axis.title.x=element_text(size=24),
          axis.title.y=element_text(size=24),
          panel.background = element_blank())
  
  p=p+geom_smooth(data=filter(d,!(subject_ID%in%no_win_subjects)), se=FALSE)
  if ( (length(no_win_subjects)>0) & length(filter(d,subject_ID%in%no_win_subjects,grepl('DDQN', agent_type))$cumulative_steps>0) ){
    p = p+geom_segment(aes(x=0,y=0,xend=max_x,yend=0),data=filter(d,subject_ID%in%no_win_subjects,grepl('DDQN', agent_type)),size=1.4)
  }
  if ( (length(no_win_subjects)>0) & length(filter(d,subject_ID%in%no_win_subjects,grepl('rainbow', agent_type))$cumulative_steps>0) ){
    p = p+geom_segment(aes(x=0,y=0.05,xend=max_x,yend=0.05),data=filter(d,subject_ID%in%no_win_subjects,grepl('rainbow', agent_type)),size=1.4)
  }
  ## there are some games where you got 0 DDQN data in short ranges of time, like 1k steps for chase.
  if (length(filter(d, grepl('DDQN', agent_type), cumulative_steps<max_x)$cumulative_steps)==0){
    p = p+geom_segment(aes(x=0,y=0,xend=max_x,yend=0,alpha=.7),data=d,size=1.4, color=colors['DDQN 100k'])
  }
  if (length(filter(d, grepl('rainbow', agent_type), cumulative_steps<max_x)$cumulative_steps)==0){
    p = p+geom_segment(aes(x=0,y=0.05,xend=max_x,yend=0.05,alpha=.7),data=d,size=1.4, color=colors['rainbow']) ## add offset so that it's visible w/ DDQN.
  }
  
  p=p+xlim(0,max_x)+ylim(0,max_y)

  if(max_x==10000){
    p=p+scale_x_continuous(breaks=c(0, 2500, 5000, 7500, 10000),labels=c('0', '2.5k', '5k', '7.5k', '10k'), limits=c(0,10000))
  }  
  if(max_x==1000000){
    p=p+scale_x_continuous(breaks=c(0, 250000, 500000, 750000, 1000000),labels=c('0', '250k', '500k', '750k', '1mil'), limits=c(0,1000000))
  }

  p = p+ theme(axis.line=element_line())
  human_kappa = filter(kappa_df, agent_type=='human')$efficiency
  EMPA_kappa = filter(kappa_df, agent_type=='EMPA')$efficiency
  DDQN_kappa = filter(kappa_df, agent_type=='DDQN 100k')$efficiency
  kappa_string = paste('Learning efficiency (\u03ba):','\nHuman: ', human_kappa, '\nEMPA: ', 
                       EMPA_kappa, '\nDDQN: ', 
                       DDQN_kappa, sep='')
  
  print(length(plots))
  plots[[k]] = p
  
  newdir=paste(getwd(),'/plots/refactor_test_curves/max=', max_x/1000, 'k/', sep='')
  dir.create(newdir, showWarnings = FALSE, recursive=TRUE)
  title = paste(newdir, game, '.png', sep='')
  ggsave(title, plot=p, width=8, height=6)
}

## produce full-page plot of all 90 games
layout = matrix(c(1:90), ncol=6, byrow=TRUE)
m = multiplot(plotlist = plots, layout=layout)
## save 50x30


## Bootstrap means and CIs in prep for figure 3

humankappadata = calculate_kappas(filter(alldata, agent_type=='human'),step_minimum=NA)
EMPAkappadata = calculate_kappas(filter(alldata, agent_type=='EMPA'),step_minimum=NA)
rEMPAkappadata = calculate_kappas(filter(alldata, agent_type=='EMPA_refactor'),step_minimum=NA)

#DDQNkappadata = calculate_kappas(filter(alldata, agent_type=='DDQN 100k'),step_minimum=NA)

kappadata = rbind(humankappadata, EMPAkappadata, rEMPAkappadata)

max_DDQNkappadata = data.frame(game_name=as.character(), agent_type=as.character(), subject_ID=as.character(), kappa=as.numeric())
non_max_DDQNkappadata = data.frame(game_name=as.character(), agent_type=as.character(), subject_ID=as.character(), kappa=as.numeric())
for (game in unique(DDQNkappadata$game_name)){
  game_data = filter(DDQNkappadata, game_name==game)
  max_DDQNkappadata = rbind(max_DDQNkappadata, filter(game_data, kappa==max(game_data$kappa)))
  non_max_DDQNkappadata = rbind(non_max_DDQNkappadata, filter(game_data, kappa!=max(game_data$kappa)))
}
non_max_DDQNkappadata$agent_type='DDQN 1k' ## hacking this to get a previously-defined light gray color in plots

means_and_CIs = bootstrap_means_and_CIs(kappadata, 'EMPA')
#EMPAmeans_and_CIs = bootstrap_means_and_CIs(kappadata, 'EMPA')
rEMPAmeans_and_CIs = bootstrap_means_and_CIs(kappadata, 'EMPA_refactor')
rEMPAmeans_and_CIs$agent_type = as.factor('EMPA_refactor')


## Refactor vs. original EMPA comparison
mean_and_CI_diffs = data.frame(game_name=as.character(), agent_type=as.character(), mean=as.numeric())
for (game in unique(means_and_CIs$game_name)){
  diff = rEMPAmeans_and_CIs[rEMPAmeans_and_CIs$game_name==game,]$mean / means_and_CIs[means_and_CIs$game_name==game,]$mean
  row = data.frame(game_name=game, agent_type='EMPA_refactor', mean=diff)
  mean_and_CI_diffs = rbind(mean_and_CI_diffs, row)
}


## Plot difference between refactor and original EMPA
main_plot_agent_types = c('EMPA_refactor', 'EMPA')
s = mean_and_CI_diffs
ordered_names = s[order(log(s$mean)),]$game_name
p = ggplot()+
  geom_bar(data=filter(mean_and_CI_diffs, agent_type%in%main_plot_agent_types & agent_type!='DDQN 100k', log(mean, 10)>-3),
           aes(x=game_name, y=log(mean), fill=as.factor(agent_type)), stat='identity', position='dodge')+
  geom_bar(data=filter(mean_and_CI_diffs, agent_type!='DDQN 100k', !log(mean, 10)>-3),
           aes(x=game_name, y=log(mean), fill=as.factor(agent_type)), alpha=1, stat='identity', position='dodge')+
  #geom_linerange(data=filter(means_and_CIs, agent_type%in%main_plot_agent_types & agent_type!='DDQN 100k', log(mean, 10)>-3),
  #              aes(x=game_name, ymin=log(low_margin), ymax=log(high_margin), fill=as.factor(agent_type)), alpha=.2, stat='identity', position='dodge')+
  # geom_point(data=non_max_DDQNkappadata,
  #            aes(x=game_name, y=log(kappa), color=agent_type), stat='identity', position='dodge', shape='|', size=3, stroke=2)+
  # geom_point(data=max_DDQNkappadata,
  #            aes(x=game_name, y=log(kappa), color=agent_type), stat='identity', position='dodge', shape='|', size=3, stroke=2)+
  scale_x_discrete(limits=ordered_names)+
  theme(axis.text.x = element_text(angle = 90, hjust = 1),legend.position='none')+ylab("Human-normed Efficiency")+xlab('Game name')+ylim(-10,10)
tickmarks = c(1e-7,1e-6, 1e-5,1e-4,1e-3,1e-2,1e-1,1e0,1e1,1e2,1e3,1e4, 1e5)
logtickmarks=(log(tickmarks))
tickmarks = c('0 (fail)', 1e-6, 1e-5,1e-4,1e-3,1e-2,1e-1,1e0,1e1,1e2,1e3,1e4, 1e5)
p=p+coord_flip()+scale_y_continuous(breaks=logtickmarks,labels=tickmarks)
p = p + theme(axis.line=element_line())+theme(panel.background = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank())
p = p+scale_fill_manual(values=colors)
p


## Human-normed figure (figure 3, but with refactored agent)
main_plot_agent_types = c('EMPA_refactor', 'EMPA')
s = filter(rEMPAmeans_and_CIs, agent_type=='EMPA_refactor')
ordered_names = s[order(log(s$mean)),]$game_name
p = ggplot()+
  geom_bar(data=filter(rEMPAmeans_and_CIs, agent_type%in%main_plot_agent_types & agent_type!='DDQN 100k', log(mean, 10)>-3),
           aes(x=game_name, y=log(mean), fill=as.factor(agent_type)), stat='identity', position='dodge')+
  geom_bar(data=filter(rEMPAmeans_and_CIs, agent_type!='DDQN 100k', !log(mean, 10)>-3),
           aes(x=game_name, y=log(mean), fill=as.factor(agent_type)), alpha=1, stat='identity', position='dodge')+
  #geom_linerange(data=filter(means_and_CIs, agent_type%in%main_plot_agent_types & agent_type!='DDQN 100k', log(mean, 10)>-3),
  #              aes(x=game_name, ymin=log(low_margin), ymax=log(high_margin), fill=as.factor(agent_type)), alpha=.2, stat='identity', position='dodge')+
  # geom_point(data=non_max_DDQNkappadata,
  #            aes(x=game_name, y=log(kappa), color=agent_type), stat='identity', position='dodge', shape='|', size=3, stroke=2)+
  # geom_point(data=max_DDQNkappadata,
  #            aes(x=game_name, y=log(kappa), color=agent_type), stat='identity', position='dodge', shape='|', size=3, stroke=2)+
  scale_x_discrete(limits=ordered_names)+
  theme(axis.text.x = element_text(angle = 90, hjust = 1),legend.position='none')+ylab("Human-normed Efficiency")+xlab('Game name')+ylim(-10,10)
tickmarks = c(1e-7,1e-6, 1e-5,1e-4,1e-3,1e-2,1e-1,1e0,1e1,1e2,1e3,1e4, 1e5)
logtickmarks=(log(tickmarks))
tickmarks = c('0 (fail)', 1e-6, 1e-5,1e-4,1e-3,1e-2,1e-1,1e0,1e1,1e2,1e3,1e4, 1e5)
p=p+coord_flip()+scale_y_continuous(breaks=logtickmarks,labels=tickmarks)
p = p + theme(axis.line=element_line())+theme(panel.background = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank())
p = p+scale_fill_manual(values=colors)
p
# p = p + scale_fill_manual(values=colors,name="Model",
# breaks=c("EMPA", "EMPA fail", "DDQN 100k"),
# labels=c("EMPA", "EMPA fail", "DDQN")) + scale_color_manual(values=colors,name="Model",
#                                                             breaks=c("EMPA", "EMPA fail", "DDQN 100k"),
#                                                             labels=c("EMPA", "EMPA fail", "DDQN"))
## 14x10


## Human-normed figure (figure 3)
main_plot_agent_types = c('EMPA_refactor', 'EMPA')
s = filter(means_and_CIs, agent_type=='EMPA')
ordered_names = s[order(log(s$mean)),]$game_name
p = ggplot()+
  geom_bar(data=filter(means_and_CIs, agent_type%in%main_plot_agent_types & agent_type!='DDQN 100k', log(mean, 10)>-3),
           aes(x=game_name, y=log(mean), fill=as.factor(agent_type)), stat='identity', position='dodge')+
  geom_bar(data=filter(means_and_CIs, agent_type!='DDQN 100k', !log(mean, 10)>-3),
           aes(x=game_name, y=log(mean), fill=as.factor(agent_type)), alpha=1, stat='identity', position='dodge')+
  #geom_linerange(data=filter(means_and_CIs, agent_type%in%main_plot_agent_types & agent_type!='DDQN 100k', log(mean, 10)>-3),
   #              aes(x=game_name, ymin=log(low_margin), ymax=log(high_margin), fill=as.factor(agent_type)), alpha=.2, stat='identity', position='dodge')+
  # geom_point(data=non_max_DDQNkappadata,
  #            aes(x=game_name, y=log(kappa), color=agent_type), stat='identity', position='dodge', shape='|', size=3, stroke=2)+
  # geom_point(data=max_DDQNkappadata,
  #            aes(x=game_name, y=log(kappa), color=agent_type), stat='identity', position='dodge', shape='|', size=3, stroke=2)+
  scale_x_discrete(limits=ordered_names)+
  theme(axis.text.x = element_text(angle = 90, hjust = 1),legend.position='none')+ylab("Human-normed Efficiency")+xlab('Game name')+ylim(-10,10)
tickmarks = c(1e-7,1e-6, 1e-5,1e-4,1e-3,1e-2,1e-1,1e0,1e1,1e2,1e3,1e4, 1e5)
logtickmarks=(log(tickmarks))
tickmarks = c('0 (fail)', 1e-6, 1e-5,1e-4,1e-3,1e-2,1e-1,1e0,1e1,1e2,1e3,1e4, 1e5)
p=p+coord_flip()+scale_y_continuous(breaks=logtickmarks,labels=tickmarks)
p = p + theme(axis.line=element_line())+theme(panel.background = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank())
p = p+scale_fill_manual(values=colors)
p
# p = p + scale_fill_manual(values=colors,name="Model",
                          # breaks=c("EMPA", "EMPA fail", "DDQN 100k"),
                          # labels=c("EMPA", "EMPA fail", "DDQN")) + scale_color_manual(values=colors,name="Model",
                          #                                                             breaks=c("EMPA", "EMPA fail", "DDQN 100k"),
                          #                                                             labels=c("EMPA", "EMPA fail", "DDQN"))
## 14x10


p = ggplot()+
  geom_bar(data=filter(rEMPAmeans_and_CIs, agent_type%in%main_plot_agent_types & agent_type!='DDQN 100k', log(mean, 10)>-3),
           aes(x=game_name, y=log(mean), fill=as.factor(agent_type)), stat='identity', position='dodge')+
  geom_bar(data=filter(rEMPAmeans_and_CIs, agent_type!='DDQN 100k', !log(mean, 10)>-3),
           aes(x=game_name, y=log(mean), fill=as.factor(agent_type)), alpha=1, stat='identity', position='dodge')+
  geom_linerange(data=filter(rEMPAmeans_and_CIs, agent_type%in%main_plot_agent_types & agent_type!='DDQN 100k', log(mean, 10)>-3),
                 aes(x=game_name, ymin=log(low_margin), ymax=log(high_margin), fill=as.factor(agent_type)), alpha=.2, stat='identity', position='dodge')+
  # geom_point(data=non_max_DDQNkappadata,
  #            aes(x=game_name, y=log(kappa), color=agent_type), stat='identity', position='dodge', shape='|', size=3, stroke=2)+
  # geom_point(data=max_DDQNkappadata,
  #            aes(x=game_name, y=log(kappa), color=agent_type), stat='identity', position='dodge', shape='|', size=3, stroke=2)+
  scale_x_discrete(limits=ordered_names)+
  theme(axis.text.x = element_text(angle = 90, hjust = 1),legend.position='none')+ylab("Human-normed Efficiency")+xlab('Game name')+ylim(-10,10)
tickmarks = c(1e-7,1e-6, 1e-5,1e-4,1e-3,1e-2,1e-1,1e0,1e1,1e2,1e3,1e4, 1e5)
logtickmarks=(log(tickmarks))
tickmarks = c('0 (fail)', 1e-6, 1e-5,1e-4,1e-3,1e-2,1e-1,1e0,1e1,1e2,1e3,1e4, 1e5)
p=p+coord_flip()+scale_y_continuous(breaks=logtickmarks,labels=tickmarks)
p = p + theme(axis.line=element_line())+theme(panel.background = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank())
p = p+scale_fill_manual(values=colors)
p



## Prep for figure 4
agents = c('EMPA', 'e-greedy 1k DS', 'e-greedy 2k DS', 'e-greedy 1k', 'e-greedy 2k', 'DDQN 100k', 'DDQN 10k', 'DDQN 1k', 'rainbow 250k', 'rainbow 150k', 'rainbow 50k', 'rainbow', 'no goal gradient', 'no subgoals + no gradient', 'no IW', 'no subgoals', 'no subgoals + no gradient + no IW')

datapoints = data.frame(x1=as.numeric(), x2=as.numeric(), x3=as.numeric(), x4=as.numeric(), x5=as.numeric(), 
                        y1=as.numeric(), y2=as.numeric(), y3=as.numeric(), mean_val=as.numeric(), agent_type=as.character(), model_cluster=as.character())
for (i in 1:length(agents)){
  agent = agents[i]
  ## Trying to just add the boxplot data manually
  quantiles = quantile(log(filter(human_normed_data, agent_type==agent)$human_normed_composite_ratio), c(.1, .25, .5, .75, .9))
  mn=mean(log(filter(human_normed_data, agent_type==agent)$human_normed_composite_ratio))
  
  q1=quantiles[1]
  q2=quantiles[2]
  q3=quantiles[3]
  q4=quantiles[4]
  q5=quantiles[5]
  if (agent == 'EMPA'){
    m_cluster = 'EMPA'
  }
  if (agent %in% c('e-greedy 1k DS', 'e-greedy 2k DS', 'e-greedy 1k', 'e-greedy 2k')){
    m_cluster = 'Exploration ablations'
  }
  if (agent%in% c('no goal gradient', 'no subgoals',  'no subgoals + no gradient',
                  'no IW', 'no subgoals + no gradient + no IW')){
    m_cluster = 'Planner ablations'
  }
  if (agent %in% c('DDQN 1k', 'DDQN 10k', 'DDQN 100k')){
    m_cluster = 'Deep RL'
  }
  if(grepl('rainbow', agent)){
    m_cluster = 'Deep RL'
  }
  if(agent=='random'){
    m_cluster = 'Random'
  }
  
  
  y1=.875
  y2=.9
  y3=.925
  ## offsets for planner lesions
  if(agent=='no subgoals'){
    y1 = y1-.06
    y2 = y2-.06
    y3 = y3-.06
  }
  if(agent=='no subgoals + no gradient'){
    y1 = y1-.12
    y2 = y2-.12
    y3 = y3-.12
  }
  if(agent=='no IW'){
    y1 = y1-.18
    y2 = y2-.18
    y3 = y3-.18
  }
  if(agent=='no subgoals + no gradient + no IW'){
    y1 = y1-.24
    y2 = y2-.24
    y3 = y3-.24
  }
  
  ## offsets for exploration lesions
  if(agent=='e-greedy 1k'){
    y1 = y1-.06
    y2 = y2-.06
    y3 = y3-.06
  }
  if(agent=='e-greedy 2k'){
    y1 = y1-.12
    y2 = y2-.12
    y3 = y3-.12
  }
  if(agent=='e-greedy 1k DS'){
    y1 = y1-.18
    y2 = y2-.18
    y3 = y3-.18
  }
  if(agent=='e-greedy 2k DS'){
    y1 = y1-.24
    y2 = y2-.24
    y3 = y3-.24
  }
  
  ##offsets for DDQN
  if(agent=='DDQN 10k'){
    y1 = y1-.06
    y2 = y2-.06
    y3 = y3-.06
  }
  if(agent=='DDQN 100k'){
    y1 = y1-.12
    y2 = y2-.12
    y3 = y3-.12
  }
  
  ##offsets for rainbow
  if(agent=='rainbow 150k'){
    y1 = y1-.18
    y2 = y2-.18
    y3 = y3-.18
  }
  
  datapoints = rbind(datapoints, data.frame(x1=q1, x2=q2, x3=q3, x4=q4, x5=q5,y1=y1, y2=y2, y3=y3, mean_val=mn, agent_type=agent,model_cluster=m_cluster))
}



df = filter(human_normed_data, agent%in%agents, (!is.na(model_cluster)&model_cluster!='Random') )
df = transform(df, agent_type=factor(agent_type, levels=c("human", "EMPA", 'e-greedy 1k', 'e-greedy 2k', 'e-greedy 1k DS', 'e-greedy 2k DS',
                                                          'no goal gradient', 'no subgoals', 'no subgoals + no gradient', 'no IW',
                                                          'no subgoals + no gradient + no IW',
                                                          'rainbow 250k', 'rainbow 150k', 'rainbow 50k', 'rainbow',
                                                          'DDQN 1k', 'DDQN 10k', 'DDQN 100k' #,
                                                          # 'random'
)))


tickmarks = c(10e-8,10e-7,10e-6, 10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
logtickmarks=(log(tickmarks))
tickmarks = c('0 (fail)',10e-7,10e-6, 10e-5,10e-4,10e-3,10e-2,10e-1,10e0,10e1,10e2,10e3,10e4)
p = ggplot(df, aes(x=log(human_normed_composite_ratio), fill=agent_type, color=agent_type))+
  geom_density(alpha=.8, adjust= 1/10)+
  scale_fill_manual(values=colors)+ scale_color_manual(values=colors)+ xlab("Human-normed Efficiency") + ylab("Density") + 
  geom_vline(xintercept=0,linetype='dashed',size=.8)+ ## originally .4
  geom_point(aes(x=mean_val, y=y2), shape=18, data=datapoints, size=7)+
  geom_segment(aes(x=x1, y=y2, xend=x2, yend=y2), linetype='longdash', data=datapoints, size=1.2)+ ##5-25
  
  geom_segment(aes(x=x2, y=y2, xend=x4, yend=y2), data=datapoints, size=1.2)+ ##25-75
  geom_segment(aes(x=x2, y=y1, xend=x2, yend=y3), data=datapoints, size=1.2)+ ##25 edge
  geom_segment(aes(x=x4, y=y1, xend=x4, yend=y3), data=datapoints, size=1.2)+ ## 75 edge
  geom_segment(aes(x=x4, y=y2, xend=x5, yend=y2), linetype='longdash', data=datapoints, size=1.2)+ ##75-95
  
  geom_segment(aes(x=x3, y=y1, xend=x3, yend=y3), data=datapoints, size=1.2)+ ##median line
  
  theme(legend.title=element_blank(), text=element_text(size=50), legend.position='none',
        axis.text.x=element_text(size=46), axis.text.y=element_text(size=46), strip.text.x=element_text(size=56))+
  theme(panel.background = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank())+
  scale_x_continuous(breaks=logtickmarks,labels=tickmarks, limits=c(logtickmarks[1], 7.5)) +
  scale_y_continuous(limits=c(0,.95), breaks=c(0,.2,.4,.6,.8), labels=c(0,.2,.4,.6,.8))+
  facet_wrap(~model_cluster, ncol=1)
p
## 30x24

## see games for which albations did better than EMPA
for (i in 1:length(scatter_data$empa_score)){
  if(scatter_data$empa_score[i] < scatter_data$model_score[i]){
    print(scatter_data[i,])
  }
}
## Reviewer 3's suggested figure 4
scatter_data = make_scatter_data(human_normed_data)
p = ggplot(scatter_data, aes(x=log(empa_score), y=log(model_score), color=model_name))+geom_point()+scale_color_manual(values=colors)+
  xlim(-20,2)+ylim(-20,2)+geom_abline(slope=1, intercept=0)
p
## Plot subjective game ratings
s = summarySE(ratings, measurevar="difficulty", groupvars=c("source_game_name","variant_number"), na.rm=TRUE)
p = ggplot(s, aes(x=reorder(variant_number, as.numeric(variant_number)), y=difficulty)) +
  geom_bar(position='dodge', stat='summary', fun.y='mean', fill='steelblue3')+geom_linerange(aes(ymin=difficulty-ci, ymax=difficulty+ci))+
  facet_wrap(~source_game_name, ncol=3)+xlab('Game variant')+ylab('Difficulty')+scale_x_discrete(breaks=c(0,1,2,3,4),labels=c('original',1,2,3,4))
p  
##save 12x6

s = summarySE(ratings, measurevar="interestingness", groupvars=c("source_game_name","variant_number"), na.rm=TRUE)
p = ggplot(s, aes(x=reorder(variant_number, as.numeric(variant_number)), y=interestingness)) +
  geom_bar(position='dodge', stat='summary', fun.y='mean', fill='steelblue3')+geom_linerange(aes(ymin=interestingness-ci, ymax=interestingness+ci))+
  facet_wrap(~source_game_name, ncol=3)+xlab('Game variant')+ylab('Interestingness') +scale_x_discrete(breaks=c(0,1,2,3,4),labels=c('original',1,2,3,4))
p  
##save 12x6


### Find median humans to pick demo videos
median_subjects = data.frame(game_name=as.character(), subject_ID=as.character())
closest_to_empa_subjects = data.frame(game_name=as.character(), subject_ID=as.character())
for (game in unique(alldata$game_name)){
  
  human_subs = filter(humandata, game_name==game)
  empa_subs = filter(EMPAdata, game_name==game, agent_type=='EMPA')
  first_empa_subj = filter(empa_subs, subject_ID==unique(empa_subs$subject_ID)[1])
  empa_kappa = calculate_kappa(first_empa_subj,NA)
  
  subjects = data.frame(subject_ID=as.character(), kappa=as.numeric())
  for (subject in unique(human_subs$subject_ID)){
    subjects = rbind(subjects, data.frame(subject_ID=subject, kappa=calculate_kappa(filter(human_subs, subject_ID==subject),NA)))
  }
  subjects = filter(subjects, !is.na(kappa))
  med = median(subjects$kappa)
  for (i in 1:length(subjects$kappa)){
    subjects$distance_to_median[i] = abs(med-subjects$kappa[i])
    subjects$distance_to_empa[i] = abs(empa_kappa-subjects$kappa[i])
    
  }
  median_subjects = rbind(median_subjects, data.frame(game_name=game, subject_ID=subjects[subjects$distance_to_median==min(subjects$distance_to_median),]$subject_ID[1]))
  closest_to_empa_subjects = rbind(closest_to_empa_subjects, data.frame(game_name=game, subject_ID=subjects[subjects$distance_to_empa==min(subjects$distance_to_empa),]$subject_ID[1]))
}


bootstrap_means_and_CIs = function(kappadata, modeltype1, modeltype2){
  ## Bootstrap 10k samples
  N=10
  M=10
  means_and_CIs = data.frame(game_name=as.character(), agent_type=as.character(), mean=as.numeric(), low_margin=as.numeric(), high_margin=as.numeric())
  for (game in unique(kappadata$game_name)){
    data1 = filter(kappadata, agent_type==modeltype1, game_name==game, !is.na(kappa))
    data2 = filter(kappadata, agent_type==modeltype2, game_name==game, !is.na(kappa))
    kappa_ratios = numeric(N)
    all_kappa_ratios = data.frame(values=as.numeric())
    ## double loop for speedup?
    for (j in 1:M){
      for (i in 1:N){
        kappas = bootstrap_kappa_ratio(data1, data2)
        kappa_ratios[i] = kappas
      }
      all_kappa_ratios = rbind(all_kappa_ratios, data.frame(values=kappa_ratios))
    }
    low_mean_high = calculate_CI(all_kappa_ratios$values)
    
    ## failure for models counts as 1e-7
    if(low_mean_high[2]==0){
      low_mean_high = c(1e-7, 1e-7, 1e-7)
    }  
    
    
    row = data.frame(game_name=game, agent_type=modeltype1, mean=low_mean_high[2], low_margin=low_mean_high[1], high_margin=low_mean_high[3])
    means_and_CIs = rbind(means_and_CIs, row)
  }
  means_and_CIs = transform(means_and_CIs, agent_type=factor(agent_type, levels=c('EMPA', 'EMPA fail')))
  
  return(means_and_CIs)
}

